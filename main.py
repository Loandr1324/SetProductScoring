# Author Loik Andrey mail: loikand@mail.ru
from config import FILE_NAME_LOG
from google_table.google_tb_work import WorkGoogle
from datetime import datetime as dt
from loguru import logger

# Задаём параметры логирования
logger.add(FILE_NAME_LOG,
           format="{time:DD/MM/YY HH:mm:ss} - {file} - {level} - {message}",
           level="INFO",
           rotation="1 week",
           compression="zip")


def remove_duplicate(data: list[dict]) -> list[dict]:
    """
    Удаляем дубли элементов списка у которых одинаковые значения ключей 'number' и 'brand'

    :param data: Список словарей в которых обязательно должны быть ключи 'number' и 'brand'
    :return: Список словарей без дубликатов по ключам словаря
    """
    # Используем множество для отслеживания уникальных комбинаций 'number' и 'brand'
    unique_keys = set()
    unique_data = []

    for item in data:
        key = (item['number'], item['brand'])
        if key not in unique_keys:
            unique_keys.add(key)
            unique_data.append(item)
    return unique_data


def filtered(products: list[dict], count_products: int, days_interval: dict) -> list[dict]:
    """
    Выбираем строки согласно правилам по ТЗ:
    1. Если "rule" установлено 0, то позиции не берём для проценки.
    2. Фильтруем позиции по коэффициенту оборачиваемости начиная с самого высокого к10.
    Если при последующих фильтрациях по цене и дате позиций отобрано не достаточно,
    то переходим к следующему коэффициенту оборачиваемости,
    пока не наберём необходимое количество позиций count_products.
    2.1. Если нет цены и дата проценки больше заданного интервала, то неважны дальнейшие поля,
    берём эти позиции в проценку.
    После того как выбрали все без цены и не набрали count_products позиций, то начинаем работать по второму приоритету.
    Если набрали количество больше, то берём первые count_products элементов.
    2.2. Если цена есть и дата проценки больше заданного интервала, то берём все эти позиции.
    Если не набрали count_products, то переходим к позициям со следующим коэффициентом оборачиваемости.

    :param count_products: Количество продуктов для отбора
    :param days_interval: dict{
        Коэффициент оборачиваемости: Количество дней от текущей даты, чтобы считать проценку устаревшей
        }
    :param products: list[dict
            ключи словаря {
            "number" - Код детали,
            "brand" - Имя производителя
            "description" - description
            "stock" - Наличие
            "price" - Цена
            "updated_date" - Дата последнего получения цены
            "turn_ratio" - Коэффициент оборачиваемости
            "norm_stock" - Норма наличия
            "rule" - Правило выбора цены
            "select_flag" - Отбор для получения цены
            "id_rule" - ID правила для получения цены
            },...]
    :return: list[dict] с теми же ключами, что и products
    """
    logger.info(f"Общее количество позиций для фильтрации: {len(products)}")

    # Фильтруем позиции по правилу
    products = [product for product in products if product['rule'] != '0']
    logger.info(f"Количество отобранных позиций разрешённых для проценки: {len(products)}")

    # Удаляем дубли позиций
    products = remove_duplicate(products)
    logger.info(f"Количество отобранных позиций для проценки после удаления дублей: {len(products)}")

    filtered_products = []
    val_count = count_products
    logger.info(f"Начинаем фильтрацию по коэффициентам оборачиваемости")
    for key in sorted(days_interval.keys(), reverse=True):
        filtered_by_turn_ratio = [product for product in products if int(product['turn_ratio']) == key]
        logger.info(f"Количество отобранных позиций до фильтрации "
                    f"по коэффициенту оборачиваемости к{key}: {len(filtered_by_turn_ratio)}")

        # Фильтруем позиции без цены
        filtered_by_price = \
            [product for product in filtered_by_turn_ratio if not product['price']
             and (dt.now() - product['updated_date']).days > int(days_interval[key])][:val_count]
        logger.info(f"Количество отобранных позиций без цены "
                    f"по коэффициенту оборачиваемости к{key}: {len(filtered_by_price)}")
        unfiltered_products = [product for product in filtered_by_turn_ratio if product not in filtered_by_price]
        logger.info(f"Количество не отфильтрованных позиций: {len(unfiltered_products)}")

        # Обновляем список отфильтрованных позиций
        filtered_products += filtered_by_price
        val_count -= len(filtered_by_price)
        logger.info(f"Осталось добавить {val_count} позиций")

        # Добавляем позиции с ценой, если позиций не достаточно
        if val_count > 0:
            logger.info("Добавляем позиции с ценой")
            # Фильтруем позиции с ценой
            filter_by_date = [product for product in unfiltered_products if product['price']
                              and (dt.now() - product['updated_date']).days > days_interval[key]][:val_count]

            logger.info(f"Количество отобранных позиций с ценой "
                        f"по коэффициенту оборачиваемости к{key}: {len(filter_by_date)}")

            filtered_products += filter_by_date
            logger.info(f"Количество элементов без цены и с ценой "
                        f"по коэффициенту оборачиваемости к{key}: {len(filtered_products)}")

            unfiltered_products = [product for product in unfiltered_products if product not in filter_by_date]
            logger.info(f"Количество не отфильтрованных позиций: {len(unfiltered_products)}")
            val_count -= len(filter_by_date)
            logger.info(f"Осталось добавить {val_count} позиций")
        logger.info(f"Итого отобрано позиций с учётом коэффициента оборачиваемости к{key}: {len(filtered_products)}")

        # Завершаем цикл, если набрали необходимое количество позиций
        if val_count <= 0:
            break

    return filtered_products


def main() -> None:
    """
    Основной процесс программы
    :return:
    """
    logger.info(f"... Запуск программы")

    # Получаем данные из Google таблицы
    wk_g = WorkGoogle()
    products = wk_g.get_products()
    count_row = len(products)

    # Получаем правила фильтрации
    rules = wk_g.get_rule_for_selected_products()

    # Фильтруем данные
    products = filtered(products, rules['count_products'], rules['days_interval'])

    # Записываем в Google таблице данные по выбранным позициям
    wk_g.set_selected_products(products, count_row, 'K')

    logger.info(f"... Окончание работы программы")


if __name__ == "__main__":
    main()
