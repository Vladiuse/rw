UNLOADING_BOOK = 'Книга выгрузки'
CALL_TO_CLIENTS_BOOK = 'Книга вывоза по клиентам'

UNLOADING_BOOK_EXAMPLE = """
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                                                                                                        Форма ГУ-44
          КHИГА ВЫГРУЗКИ ГРУЗОВ (НЕВЫВЕЗЕННЫЕ ГРУЗЫ)          ГУ-44 все отправки                              18.02.2025 08:36
          НА СТАНЦИИ XXXXXXXXX                                                                                 КОНТЕЙНЕРНАЯ ПЛ
          за 18.02.2025                                                                                       Лист 2
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  NN  │N вагона│ N отправки │наименован.ст.│Nконтейнера/пр│ наименование гр.│вес(кг)│коорди-│   получатель  │дата,время│ приемо-сдатчик
 п/п  │        │            │дороги отправл│              │ опасность груза │ груза │ наты  │               │ выгрузки │   примечание 
       п о п у т н ы е  а к т ы       п р и м е ч а н и е 
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 39870 91767257 34464995     ЗАМОСКОВСКК КЖ AICU6751350/99 ПРЕДПРИЯТИЕ "XX"      5256  37 152ЧТУП СУПЕР-МИКС 20.10.2024 Пупкин Полина Вл
                             ЗАБ                                                             ОПТИМАЛЬНЫЙ ХАБ 15:30
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ 
 39471 91767257 34465053     ЗАМОСКОВСКК КЖ AICU6751540/99 ПРЕДПРИЯТИЕ "XX"      5175        ЧТУП СУПЕР-МИКС 20.10.2024 Пупкин Полина Вл
                             ЗАБ                                                             ОПТИМАЛЬНЫЙ ХАБ 15:30
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ 
 39304 98667111 34465007     ЗАМОСКОВСКК КЖ AICU6751392/99 ПРЕДПРИЯТИЕ "XX"      5355  16 142ЧТУП СУПЕР-МИКС 20.10.2024 Пупкин Полина Вл
"""

CALL_TO_CLIENTS_BOOK_EXAMPLE = """
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                                                                                                        Форма ГУ-44
          КHИГА ВЫГРУЗКИ ГРУЗОВ (ВЫВЕЗЕННЫЕ ГРУЗЫ)                                                            16.01.2025 01:12
          НА СТАНЦИИ XXXXXXXXX                                                                                 КОНТЕЙНЕРНАЯ ПЛ
          за период с 01.01.2024 00:01 по 31.12.2024 до 23:59                                                 Лист 1
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
N п/п │Nконтейнера│ N отправки │ время выгрузки │  время вывоза  │наим.гр.-оп.│получатель│   N наряда   │N пропуска│автомобиль│ пр-сд.
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 45338 AICU8111732 33021781     22.12.2023 22:30 01.01.2024 15:25 МОТОЦИКЛЫ XX ООО ЗАВОДХ 48467/47338               XT2521-7   Пупкина АВ
 46339 BYGU4021998 33021772     22.12.2023 22:30 01.01.2024 15:30 МОТОЦИКЛЫ XX ООО ЗАВОДХ 48466/47339               HT2472-5   Пупкина АВ
 48375 AHTU4100456 33142146     30.12.2023 06:30 02.01.2024 10:00 ПРОЧИЕ ГРУЗЫ РУП СУППОЧ 49605/48375                          Пупкина К 
"""
BOOK_EXAMPLES = {
    UNLOADING_BOOK: UNLOADING_BOOK_EXAMPLE,
    CALL_TO_CLIENTS_BOOK: CALL_TO_CLIENTS_BOOK_EXAMPLE,
}
