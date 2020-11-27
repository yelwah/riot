import xlsxwriter
from typing import List, Any

def outputToExcel(filename: str, headings: List[str] = None, rowContent: List[List[Any]] = None, contentDict: List[dict] = None):
  '''Takes a list of heading names, then a list of rows contening a list of column values, and 
  outputs it to an excel file
  '''
  workbook = xlsxwriter.Workbook('output/' + filename + '.xlsx')
  worksheet = workbook.add_worksheet()

  if headings is not None and rowContent is not None:
    for i in range(len(headings)):
      worksheet.write(0, i, headings[i])

    for rowIndex in range(len(rowContent)):
      for columnIndex in range(len(rowContent[rowIndex])):
        worksheet.write(rowIndex+1, columnIndex, rowContent[rowIndex][columnIndex])

  if contentDict is not None:
    # Extract column headings
    firstDict = contentDict[0]
    column = 0
    for key in firstDict:
      worksheet.write(0, column, key)
      column += 1
  
    for row in range(len(contentDict)):
      column = 0
      for key, value in contentDict[row].items():
        worksheet.write(row+1, column, value)
        column += 1
  workbook.close()