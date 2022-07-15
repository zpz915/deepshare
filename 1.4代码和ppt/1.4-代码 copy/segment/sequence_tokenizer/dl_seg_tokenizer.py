from segment.model.bilstm_crf.bilstm_crf_predictor import BiLSTMCRFPredictor
from segment.sequence_tokenizer.sequence_seg_tokenizer import SequenceSegTokenizer
from segment.sequence_result_parser import SequenceResultParser


class DLSegTokenizer(SequenceSegTokenizer):
    """docstring for DLCutTokenizer."""

    def __init__(self, model_path):
        super(DLSegTokenizer, self).__init__()
        self._predictor = BiLSTMCRFPredictor(model_path)

    def _tag(self, content):
        labels = self._predictor.predict([content])[0]
        return SequenceResultParser.parse(content, labels)
