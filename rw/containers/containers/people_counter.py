import re
# from .containers import Container


# class PeopleCounter:
#
#     def __init__(self, text):
#         self.text = text
#         self.people_lines = []
#         self.no_people = []
#         self.GENERAL_COUNT = 0
#         self.UNIQUE_CONTR = set()
#         self.res = []
#
#     def res_text(self):
#         return '\n'.join(self.res)
#
#     def proccess(self):
#         for line in self.text.split('\n'):
#             res_vagon = re.search(r'[A-Z]{4}\d{7}', line)
#             res_date = re.search(r'\d{1,2}\.\d{1,2}\.\d{1,4}', line)
#             if res_vagon and res_date:
#                 self.people_lines.append(line)
#                 self.UNIQUE_CONTR.add(line[93:109])
#             else:
#                 self.no_people.append(line)
#         names_n_count = []
#         for name in self.UNIQUE_CONTR:
#             res = [name, self.text.count(name)]
#             names_n_count.append(res)
#
#         names_n_count.sort(key=lambda x: x[1], reverse=True)
#         for name, count in names_n_count:
#             self.GENERAL_COUNT += count
#             self.res.append(f'{name} : {count}')




