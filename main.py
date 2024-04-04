# Author Loik Andrey mail: loikand@mail.ru
from config import FILE_NAME_LOG, COUNT_PRODUCTS, DAYS_INTERVAL
from google_table.google_tb_work import WorkGoogle
from datetime import datetime as dt
from loguru import logger

# Задаём параметры логирования
logger.add(FILE_NAME_LOG,
           format="{time:DD/MM/YY HH:mm:ss} - {file} - {level} - {message}",
           level="INFO",
           rotation="1 week",
           compression="zip")


def filtered(products: list[dict]) -> list[dict]:
    """
    Выбираем строки согласно правилам по ТЗ:
    1. Если нет цены, то неважны дальнейшие поля. Берём эту позицию в проценку.
    После того как выбрали все без цены и не набрали COUNT_PRODUCTS позиций, то начинаем работать по второму приоритету.
    Если на первом шаге набираем больше COUNT_PRODUCTS, то выбираем с наибольшей оборачиваемостью,
    но не больше COUNT_PRODUCTS.
    2. Если цена есть и срок проценки больше заданной, то берём все эти позиции.
    Если не набрали COUNT_PRODUCTS, то переходим к третьему приоритету.
    Если на первом шаге набираем больше чем не хватает до COUNT_PRODUCTS,
    то выбираем с наибольшей оборачиваемостью количество, которого не хватает до COUNT_PRODUCTS.
    3. Если цена есть, срок находится в допустимом интервале, то выбираем позиции по оборачиваемости.
    Берём позиции с большей оборачиваемостью и идём по убыванию, пока не наберём COUNT_PRODUCTS,
    или пока не закончатся позиции.

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
    filtered_products = sorted([product for product in products if not product['price']],
                               key=lambda x: float(x['turn_ratio'] or 0), reverse=True)[:COUNT_PRODUCTS]
    logger.info(f"Первый этап. Количество отобранных позиций без цены: {len(filtered_products)}")

    unfiltered_products = [product for product in products if product not in filtered_products]
    logger.info(f"Количество не отфильтрованных позиций: {len(unfiltered_products)}")

    # Добавляем позиции с ценой, если позиций не достаточно
    val_count = COUNT_PRODUCTS - len(filtered_products)
    if val_count > 0:
        logger.info("Добавляем позиции с ценой")
        filter_by_date = [product for product in unfiltered_products if product['price']]

        logger.info(f"Количество позиций с ценой: {len(filter_by_date)}")
        filter_by_date = sorted(
            [product for product in filter_by_date if (dt.now() - product['updated_date']).days > DAYS_INTERVAL],
            key=lambda x: float(x['turn_ratio'] or 0), reverse=True)[:val_count]
        logger.info(f"Второй этап. Количество отобранных позиций с ценой: {len(filter_by_date)}")

        filtered_products += filter_by_date
        logger.info(f"Количество элементов без цены и с ценой {len(filtered_products)}")

        unfiltered_products = [product for product in unfiltered_products if product not in filter_by_date]
        logger.info(f"Количество не отфильтрованных позиций: {len(unfiltered_products)}")

    # Добавляем позиции из всего списка по оборачиваемости, если позиций не достаточно
    val_count = COUNT_PRODUCTS - len(filtered_products)
    if val_count > 0:
        logger.info("Добавляем позиции по оборачиваемости")
        filter_by_turn_ratio = sorted([product for product in unfiltered_products],
                                      key=lambda x: float(x['turn_ratio'] or 0), reverse=True)[:val_count]
        logger.info(f"Третий этап. Количество отобранных позиций по оборачиваемости: {len(filter_by_turn_ratio)}")
        unfiltered_products = [product for product in unfiltered_products if product not in filter_by_turn_ratio]
        logger.info(f"Количество не отфильтрованных позиций: {len(unfiltered_products)}")

    logger.info(f"Итоговое количество отобранных позиций: {len(filtered_products)}")
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

    # Фильтруем данные
    products = filtered(products)

    # Записываем в Google таблице данные по выбранным позициям
    wk_g.set_selected_products(products, count_row)

    logger.info(f"... Окончание работы программы")


if __name__ == "__main__":
    main()
