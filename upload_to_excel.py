import openpyxl


def upload_to_excel(data, filename):
    try:
        wb = openpyxl.Workbook()
        ws = wb.active

        for row in data:
            ws.append(row)

        wb.save(filename)
    except Exception as e:
        print(f"An error occurred while writing to excel: {str(e)}")
        raise e
