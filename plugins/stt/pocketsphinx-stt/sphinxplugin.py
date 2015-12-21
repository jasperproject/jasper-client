import os.path
import logging
import tempfile
from jasper import plugin
from . import sphinxvocab
try:
    try:
        import pocketsphinx
    except ValueError:
        # Fixes a quirky bug when first import doesn't work.
        # See http://sourceforge.net/p/cmusphinx/bugs/284/ for details.
        import pocketsphinx
    pocketsphinx_available = True
except ImportError:
    pocketsphinx = None
    pocketsphinx_available = False


class PocketsphinxSTTPlugin(plugin.STTPlugin):
    """
    The default Speech-to-Text implementation which relies on PocketSphinx.
    """

    def __init__(self, *args, **kwargs):
        """
        Initiates the pocketsphinx instance.

        Arguments:
            vocabulary -- a PocketsphinxVocabulary instance
            hmm_dir -- the path of the Hidden Markov Model (HMM)
        """
        plugin.STTPlugin.__init__(self, *args, **kwargs)

        self._logger = logging.getLogger(__name__)
        self._logfile = None

        if not pocketsphinx_available:
            raise ImportError("Pocketsphinx not installed!")

        self._logger.warning("This STT plugin doesn't have multilanguage " +
                             "support!")

        vocabulary_path = self.compile_vocabulary(
            sphinxvocab.compile_vocabulary)

        lm_path = sphinxvocab.get_languagemodel_path(vocabulary_path)
        dict_path = sphinxvocab.get_dictionary_path(vocabulary_path)

        hmm_dir = self.config.get('pocketsphinx', 'hmm_dir')
        if not hmm_dir:
            hmm_dir = "/usr/local/share/pocketsphinx/model/hmm/en_US/" + \
                      "hub4wsj_sc_8k"

        self._logger.debug("Initializing PocketSphinx Decoder with hmm_dir " +
                           "'%s'", hmm_dir)

        # Perform some checks on the hmm_dir so that we can display more
        # meaningful error messages if neccessary
        if not os.path.exists(hmm_dir):
            msg = ("hmm_dir '%s' does not exist! Please make sure that you " +
                   "have set the correct hmm_dir in your profile.") % hmm_dir
            self._logger.error(msg)
            raise RuntimeError(msg)
        # Lets check if all required files are there. Refer to:
        # http://cmusphinx.sourceforge.net/wiki/acousticmodelformat
        # for details
        missing_hmm_files = []
        for fname in ('mdef', 'feat.params', 'means', 'noisedict',
                      'transition_matrices', 'variances'):
            if not os.path.exists(os.path.join(hmm_dir, fname)):
                missing_hmm_files.append(fname)
        mixweights = os.path.exists(os.path.join(hmm_dir, 'mixture_weights'))
        sendump = os.path.exists(os.path.join(hmm_dir, 'sendump'))
        if not mixweights and not sendump:
            # We only need mixture_weights OR sendump
            missing_hmm_files.append('mixture_weights or sendump')
        if missing_hmm_files:
            self._logger.warning("hmm_dir '%s' is missing files: %s. Please " +
                                 "make sure that you have set the correct " +
                                 "hmm_dir in your profile.",
                                 hmm_dir, ', '.join(missing_hmm_files))

        self._pocketsphinx_v5 = hasattr(pocketsphinx.Decoder, 'default_config')

        with tempfile.NamedTemporaryFile(prefix='psdecoder_',
                                         suffix='.log', delete=False) as f:
            self._logfile = f.name

        if self._pocketsphinx_v5:
            # Pocketsphinx v5
            config = pocketsphinx.Decoder.default_config()
            config.set_string('-hmm', hmm_dir)
            config.set_string('-lm', lm_path)
            config.set_string('-dict', dict_path)
            config.set_string('-logfn', self._logfile)
            self._decoder = pocketsphinx.Decoder(config)
        else:
            # Pocketsphinx v4 or sooner
            self._decoder = pocketsphinx.Decoder(
                hmm=hmm_dir, logfn=self._logfile, lm=lm_path, dict=dict_path)

    def __del__(self):
        if self._logfile is not None:
            os.remove(self._logfile)

    def transcribe(self, fp):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
            fp -- a file object containing audio data
        """

        fp.seek(44)

        # FIXME: Can't use the Decoder.decode_raw() here, because
        # pocketsphinx segfaults with tempfile.SpooledTemporaryFile()
        data = fp.read()
        self._decoder.start_utt()
        self._decoder.process_raw(data, False, True)
        self._decoder.end_utt()

        if self._pocketsphinx_v5:
            hyp = self._decoder.hyp()
            result = hyp.hypstr if hyp is not None else ''
        else:
            result = self._decoder.get_hyp()[0]
        if self._logfile is not None:
            with open(self._logfile, 'r+') as f:
                for line in f:
                    self._logger.debug(line.strip())
                f.truncate()

        transcribed = [result] if result != '' else []
        self._logger.info('Transcribed: %r', transcribed)
        return transcribed
