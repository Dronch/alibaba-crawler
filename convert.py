import xlsxwriter
import os
import sys
from tqdm import tqdm


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: {} <input.csv> <output.xlsx>'.format(sys.argv[0]))
        exit()

    items = open(sys.argv[1]).read().splitlines()
    workbook = xlsxwriter.Workbook(sys.argv[2])
    worksheet = workbook.add_worksheet()
    worksheet.set_default_row(120)
    worksheet.set_column('A:B', 40)
    worksheet.set_column('C:Z', 20)

    current_row = 1
    for item in tqdm(items):
        cols = item.split(';')
        worksheet.write('A{}'.format(current_row), cols[0])
        worksheet.write('B{}'.format(current_row), cols[1])
        worksheet.write('C{}'.format(current_row), cols[2])
        worksheet.write('D{}'.format(current_row), cols[3])
        worksheet.write('E{}'.format(current_row), cols[4])
        cols = cols[5:]
        img_urls = cols[0:][::2]
        img_files = cols[1:][::2]
        n = len(img_files)
        char = 'F'
        for i in range(n):
            worksheet.insert_image('{}{}'.format(char, current_row),
                                   os.path.join('images', img_files[i]),
                                   {
                                       'url': img_urls[i],
                                       'x_scale': 1 / 5.5,
                                       'y_scale': 1 / 5.5,
                                       'x_offset': 5,
                                       'y_offset': 5
                                   })
            char = chr(ord(char) + 1)
        current_row += 1

    workbook.close()
