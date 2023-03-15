import docx2txt
import textract

def read_by_docx2txt(path):
    text = docx2txt.process(path)
    return text


def read_by_textract(path):
    text = textract.process(path)
    text = text.decode('utf-8')
    return text


def read_word_doc(path):
    for reader in read_by_docx2txt, read_by_textract:
        try:
            text = reader(path)
            return text
        except BaseException as error:
            # print(reader)
            # print(error)
            pass
    return