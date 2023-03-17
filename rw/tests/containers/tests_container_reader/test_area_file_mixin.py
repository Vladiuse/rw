import unittest
from rw.containers.containers.file import AreaFileMixin, AreaFile
from rw.containers.containers.errors import AreaFileError



class AreaFileMixinTest(unittest.TestCase):

    def setUp(self) -> None:
        text = """
════════════════════════════════════════════════════════════════════════════════

Контейнера, установленные на площадке   17.03.2023
секции: 1 - 99                          15:20
────────────────────────────────────────────────────────────────────────────────
коорд.│ N контейнера  │сост.│  п л о м б ы
────────────────────────────────────────────────────────────────────────────────
 1 111 DLRU0108549 /99 груж. 081895                   005208
 1 112 TKRU4336174 /99 груж. 084095
 1 121 TKRU4110551 /99 груж. 192385                   21914
 1 122 SLZU2560149 /99 груж. 
 1 123 SUDU7351691 /99 пор.  
 1 131 TDLU6227305 /99 груж. 593911  
   
        """
        self.area_file  = AreaFile(text=text)


    def test_get_area_from_row(self):
        row = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'
        self.assertEqual(AreaFileMixin.get_area(row),1)

    def test_get_area_from_row_two_number_area(self):
        row = '49 341 GAWU7005200 /99 пор.  '
        self.assertEqual(AreaFileMixin.get_area(row),49)

    def test_raise_error_incorrect_area(self):
        row = '49341GAWU7005200 /99 пор.  '
        with self.assertRaises(AreaFileError):
            self.area_file.get_area(row)


    def test_get_data_from_row_valid_type(self):
        line = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'
        is_valid_data = AreaFileMixin.get_data_from_row(line)
        self.assertTrue(isinstance(is_valid_data, dict))

    def test_correct_find_values(self):
        line = ' 1 111 DLRU0108549 /99 груж. 081895                   005208'
        is_valid_data = AreaFileMixin.get_data_from_row(line)
        self.assertEqual(is_valid_data['container'],'DLRU0108549')
        self.assertEqual(is_valid_data['area'],1)

    def test_get_data_from_row_valid_type_invalid(self):
        line = ' 1 111 DLR--108549 /99 груж. 081895                   005208'
        is_valid_data = AreaFileMixin.get_data_from_row(line)
        self.assertIsNone(is_valid_data)

    def test_get_data_from_text_area_data(self):
        result = self.area_file.get_data_from_text()
        area_data = result['data']
        self.assertEqual(len(area_data), 6)

    def test_get_data_from_text_no_data_rows(self):
        result = self.area_file.get_data_from_text()
        area_data = result['data']
        rows_without_data = result['rows_without_data']
        text_rows_count = len(self.area_file.get_text().split('\n'))
        self.assertEqual(len(rows_without_data), text_rows_count - len(area_data))




if __name__ == '__main__':
    unittest.main()


