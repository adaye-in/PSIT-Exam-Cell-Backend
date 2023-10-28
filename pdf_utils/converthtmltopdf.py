from PyPDF2 import PaperSize, PdfReader, PdfMerger, PdfWriter
from datetime import datetime
from os import remove as RemoveFile
import os
import pdfkit
import json
from io import BytesIO
from PSITExamCellBackend.settings import *

PaperSize = {
    "A4": {"width": 210, "height": 297}
}

# Configuring pdfkit to point to our installation of wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")


def addParentDiv(child):
    return f''' 
    <div style="font-family: Arial;">
    {child}
    </div>
'''


def getPageString(pageNumber):
    page = f"""
<html>
<head>
</head>
<body>
    <div class="container">
        <h1>Page {pageNumber}</h1>
        <p>This is the content of page {pageNumber}.</p>
    </div>
</body>
</html>
"""
    return page


def getMatrixString(dataArr, gapStr, showBranches):
    divStyleCenter = "width: 100%; display: flex; justify-content: center;align-items:center"
    tableStyle = "width:100%;background-color:white;border-collapse:collapse;"
    outputStr = f'<div style="{divStyleCenter}"><table style="{tableStyle}"><tbody style="width:100%">'
    usingWidth = PaperSize["A4"]["height"] - 10
    usingHeight = PaperSize["A4"]["width"] - 10
    cellHeight = 40
    cellPadding = "10px 0px"
    cellWidth = usingHeight / len(dataArr[0])


    gapArr = gapStr.split("*")
    comm_arr = []
    curr = 0

    for elem in gapArr:
        curr_elem = int(elem)
        comm_arr.append(curr_elem + curr - 1)
        curr = curr_elem + curr


    comm_arr.pop()

    branchesString = ""

    for rows in range(len(dataArr)):
        outputStr += '<tr style="width:100%">'
        for cols in range(len(dataArr[rows])):
            right_gap = 0
            if (cols in comm_arr):
                right_gap = 20

            if (showBranches):
                branchesString = f'<br><span>{dataArr[rows][cols]["section_name"]}<span>'

            if dataArr[rows][cols]["student_roll"] is not None and dataArr[rows][cols] is not None:
                outputStr += f'''
                      <td style="padding:0;padding-right:{right_gap}px;margin:0">
                        <div style="border:1px solid black;min-width:{cellWidth}px;padding:{cellPadding};text-align:center">
                          <span>{dataArr[rows][cols]["student_roll"]}<span>
                          {branchesString}
                        </div>
                      </td>
                      '''
            else:
                outputStr += f'''
                      <td style="padding:0;padding-right:{right_gap}px;margin:0">
                        <div style="border:1px solid black;min-width:{cellWidth}px;padding:{cellPadding};text-align:center">
                          <span>N/A<span>
                          <br><span>--<span>
                        </div>
                      </td>
                      '''

        outputStr += '</tr>'
    outputStr += '</tbody></table></div>'
    return outputStr


def getSectionWiseStudents(dataArr):
    sectionObj = {}
    for rows in range(len(dataArr[0])):
        for cols in range(len(dataArr)):
            dataCell = dataArr[cols][rows]
            if dataCell is not None and dataCell['student_roll'] is not None:
                temp = [dataCell["student_roll"], dataCell["student_name"], dataCell["isDetained"]]
                if (dataCell["section_name"] in sectionObj):
                    sectionObj[dataCell["section_name"]].append(temp)
                else:
                    sectionObj[dataCell["section_name"]] = [temp]
    return sectionObj


def getMatrixFooter(SectionWiseStudents):
    gap = 40
    divStyleCenter = f"width: 100%; display: flex; justify-content: center;align-items:center;padding-top:{gap}px"
    tableStyle = "width:100%;background-color:white;border-collapse:collapse;"
    usingWidth = PaperSize["A4"]["height"] - 10
    usingHeight = PaperSize["A4"]["width"] - 10
    cellPadding = "10px 0px"
    cellWidth = usingHeight / len(SectionWiseStudents.keys()) + 1
    outputStr = f'<div style="{divStyleCenter}"><table style="{tableStyle}"><tbody style="width:100%">'
    outputStr += '<tr>'

    for i in SectionWiseStudents.keys():
        outputStr += f'''
            <th style="border:1px solid black;min-width:{cellWidth}px;padding:{cellPadding};text-align:center">{i}</th>
        '''

    outputStr += f'''
            <th style="border:1px solid black;min-width:{cellWidth}px;padding:{cellPadding};text-align:center">Total</th>
    '''

    outputStr += '</tr>'
    outputStr += '<tr>'
    total_students = 0

    for i in SectionWiseStudents.keys():
        total_students += len(SectionWiseStudents[i])
        outputStr += f'''
            <td style="border:1px solid black;min-width:{cellWidth}px;padding:{cellPadding};text-align:center">{len(SectionWiseStudents[i])}</td>
        '''

    outputStr += f'''
            <td style="border:1px solid black;min-width:{cellWidth}px;padding:{cellPadding};text-align:center">{total_students}</td>
        '''

    outputStr += '</tr>'
    outputStr += '</tbody></table></div>'
    return outputStr


def getMatrixHeader(dataObj):
    gapBottom = 20
    gapEach = 10
    divStyleParent = f"width: 100%; display: flex; justify-content: center;align-items:center;padding-bottom:{gapBottom}px;flex-direction:column;text-align:center;font-size:20;font-weight:600"
    divStyleBlock = f"width: 100%;background-color:black;color:white;margin-bottom:{gapEach}px;padding:5px"
    outputStr = f'<div style="{divStyleParent}">'
    outputStr += f'<div style="{divStyleBlock}"><span>{dataObj["room_number"]}</span></div>'
    outputStr += f'<div style=""><span>Black Board</span></div>'
    outputStr += '</div>'
    return outputStr


def getAttendanceHeader(session, branch, room_number):
    gapBottom = 20
    gapEach = 10
    divStyleParent = f"width: 100%; display: flex; justify-content: center;align-items:center;padding-bottom:{gapBottom}px;flex-direction:column;text-align:center;font-size:20;font-weight:600"
    divStyleBlock = f"width: 100%;background-color:black;color:white;margin-bottom:{gapEach}px;padding:5px"
    outputStr = f'<div style="{divStyleParent}">'
    outputStr += f'<div style="{divStyleBlock}"><span>PRANVEER SINGH INSTITUTE OF TECHNOLOGY, KANPUR</span></div>'
    outputStr += f'<div style=""><span>{session}</span></div>'
    outputStr += f'''
    <table style="width:100%;padding:8px 0px">
      <tbody style="width:100%">
        <th style="width:30%;text-align:left;">Date :</th>
        <th style="width:30%;text-align:left;">Time :</th>
        <th style="width:30%;text-align:left;">Subject Code :</td>
      </tbody>
    </table>
    '''
    outputStr += f'<div style=""><span>{branch} ( {room_number} )</span></div>'
    outputStr += '</div>'
    return outputStr


def getAttendanceFooter(students):
    gapTop = 20
    rowGap = 8

    outputStr = f''
    outputStr += f'''
    <table style="width:100%;margin-top:{gapTop}px;font-family: Arial;border-collapse: separate; border-spacing: 0 {rowGap}px;">
      <tbody style="width:100%">
        <tr style="">
          <td style="width:70%;text-align:left;">Total no. of students: {len(students)}</td>
          <td style="width:30%;text-align:left;">Present count :</td>
        </tr>
        <tr>
          <td style="width:70%;text-align:left;">Roll no. of absent Students: </td>
          <th style="width:30%;text-align:left;">Name & signature of Invigilators</th>
        </tr>
      </tbody>
    </table>
    '''

    return outputStr


def getAttendanceString(students):
    divStyleCenter = "width: 100%; display: flex; justify-content: center;align-items:center"
    tableStyle = "width:100%;background-color:white;border-collapse:collapse;"
    cellStyle = f'padding:0;margin:0;border:1px solid black;padding:4px 9px'
    outputStr = f'<div style="{divStyleCenter}"><table style="{tableStyle}"><tbody style="width:100%">'

    outputStr += f'''
    <tr>
    <th style="{cellStyle};min-width:50px;">S No.</th>
    <th style="{cellStyle};min-width:150px;">Roll Numbers</th>
    <th style="{cellStyle};width:100%">Name</th>
    <th style="{cellStyle};min-width:150px;">ID Card (Yes / No)</th>
    <th style="{cellStyle};min-width:150px;">Signature</th>
    </tr>
  '''

    for index in range(len(students)):
        outputStr += '<tr style="width:100%">'
        detained = ""
        if (students[index][2] == True):
            detained = "Detained"
        outputStr += f'''
      <td style="{cellStyle}">
        {index + 1}
      </td>
      <td style="{cellStyle}">
        {students[index][0]}
      </td>
      <td style="{cellStyle}">
        {students[index][1]}
      </td>
      <td style="{cellStyle}">
        {detained}
      </td>
      <td style="{cellStyle}">
      </td>
    '''

        outputStr += '</tr>'
    outputStr += '</tbody></table></div>'
    return outputStr


def createMatrixPage(RoomObject, path, pathsAll, showBranches=False, fileName="Matrix"):
    Result = ""

    Result += getMatrixHeader(RoomObject)
    Result += getMatrixString(RoomObject["seating_map"], RoomObject["room_breakout"], showBranches)
    Result = addParentDiv(Result);

    SectionWiseStudents = getSectionWiseStudents(RoomObject["seating_map"])
    Result += getMatrixFooter(SectionWiseStudents)
    PathFinal = f"{path}/{fileName}.pdf"

    pathsAll.append(PathFinal)
    options = {'orientation': 'Landscape'}
    # pdfkit.from_string(Result, PathFinal, configuration=config, options=options)
    pdf = pdfkit.from_string(Result, False, configuration=config, options=options)
    return pdf
    # pdf_writer.append(PdfReader(BytesIO(pdf)))


def createAttendancePage(students, branch, session, room_number, path, fileName, pathsAll):
    Result = ""

    Result += getAttendanceHeader(session, branch, room_number)
    Result += getAttendanceString(students)
    Result += getAttendanceFooter(students)

    Result = addParentDiv(Result)

    PathFinal = f"{path}/{fileName}.pdf"

    pathsAll.append(PathFinal)
    options = {'orientation': 'Portrait'}
    # pdfkit.from_string(Result, PathFinal, configuration=config, options=options)
    pdf = pdfkit.from_string(Result, False, configuration=config, options=options)
    return pdf


def createAttendancePageAll(RoomObject, pathFile, pathsAll, baseFileName="Attendance"):
    SectionWiseStudents = getSectionWiseStudents(RoomObject["seating_map"])
    pages_list = []
    for keys in SectionWiseStudents.keys():
        studentsObj = SectionWiseStudents[keys]
        FileName = f"{baseFileName}_{keys}"
        pdf = createAttendancePage(studentsObj, keys, RoomObject["session_name"], RoomObject["room_number"], pathFile,
                             FileName, pathsAll)
        pages_list.append(pdf)

    return pages_list


def begin_pdf(MockData,showBranches=True):
    basicPath = "./output"
    finalFileName = "".join(f'{MockData["session_name"]}_{MockData["room_number"]}'.split(" "))
    pdf_writer = PdfWriter()
    pathsAll = []
    pdf = createMatrixPage(RoomObject=MockData, path=basicPath, pathsAll=pathsAll, showBranches=True)
    pdf_list = createAttendancePageAll(RoomObject=MockData, pathFile=basicPath, pathsAll=pathsAll)

    pdf_writer.append(PdfReader(BytesIO(pdf)))

    for i in pdf_list:
        pdf_writer.append(PdfReader(BytesIO(i)))

    output_pdf_io = BytesIO()
    pdf_writer.write(output_pdf_io)
    return [output_pdf_io, finalFileName]
