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
    Выбираем строки согласно правилам по ТЗ
    :param products:
    :return:
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
    logger.info(f"... Запуск программы")

    # Получаем данные из Google таблицы
    wk_g = WorkGoogle()
    products = wk_g.get_products()
    count_row = len(products)

    # Фильтруем данные
    products = filtered(products)

    # Делаем запись в Google таблице по выбранным позициям
    wk_g.set_selected_products(products, count_row)

    logger.info(f"... Окончание работы программы")


if __name__ == "__main__":
    main()