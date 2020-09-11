# author : charlie
# time : 20200715
# usage : to format the xvg file generated by GROMACS.
#       After run this script, a formmatted xvg/csv file will be generated.
# command : python xvg_format.py inputfile1.xvg inputfile2.xvg
#   add '-c' could make it generate csv data file more.


import sys
import time


def write_standard(line, file_output):
    with open(file_output, 'a', encoding='utf-8') as fo:
        line = line.strip(",")
        fo.write(line + '\n')


def format_style(file_input):
    file_output = file_input + '_formatted.xvg'
    with open(file_input, 'r', encoding='utf-8') as fo:
        content = fo.read()
    lines = content.split('\n')
    # write_standard("## standard -> " + lines[0], file_output)
    title_origin = lines[1].split()
    title_deal = []
    for title_o in title_origin:
        if '(' == title_o[0]:
            title_deal[-1] += title_o.strip()
        elif '.' == title_o.strip()[-1] and '.' == title_deal[-1][-1]:
            # print(title_o)
            title_deal[-1] += title_o.strip()
            # print(title_deal)
        else:
            title_deal.append(title_o)
    title_line = ""
    for title in title_deal:
        title_line += "{:>20},".format(title)
    write_standard(title_line, file_output)
    for line in lines[2:]:
        line_lis = line.split()
        write_content = ""
        for li in line_lis:
            write_content += "{:>20.2f},".format(float(li))
        write_standard(write_content, file_output)

    print(file_output + " done ~")


def format_xvg(file_input):
    file_output = file_input.split('.')[0] + '_formatted.xvg'
    with open(file_input, 'r', encoding='utf-8') as fo:
        content = fo.read()
    lines = content.strip().strip('\n').split('\n')
    data = []
    title_line = []
    xaxis = ''
    yaxis = ''
    for line in lines:
        if line[0] == '#':
            pass
        elif line[0] == '@':
            if '@' in line and 'xaxis' in line:
                xaxis = line.strip('"').split('"')[-1].replace(' ', '')
                title_line.append(xaxis)
            elif '@' in line and 'yaxis' in line:
                yaxis = line.strip('"').split('"')[-1].replace(' ', '')
            elif '@ s' in line and 'legend' in line:
                title_line.append(
                    line.strip('"').split('"')[-1].replace(' ', ''))
        else:
            try:
                float(line.split()[0])
            except:
                # 针对行首非数字的情况，以two spaces作为间隔split并构建title_line
                title_line = [item.replace(' ', '')
                              for item in line.split('  ') if item != '']
            else:
                data.append(line.split())
    if len(title_line) == 1:
        title_line.append(yaxis)
    # print(title_line)
    with open(file_output, 'w', encoding='utf-8') as fo:
        fo.write(
            '# this file is generated by xvg_format.py from {} at {}\n'.format(
                file_input, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        fo.write('# xaxis : {0}   yaxis : {1}\n'.format(xaxis, yaxis))
        title_write = ""
        for title in title_line:
            title_write += "{:>16}".format(title)
        fo.write(title_write + '\n')
        for cols in data:
            cols_write = ""
            for col in cols:
                cols_write += "{:>16.2f}".format(float(col))
            fo.write(cols_write + '\n')
    print(" {} Write done~ ".format(file_input))


def format_csv(file_input):
    format_xvg(file_input)
    file_output = file_input.split('.')[0] + '_formatted.xvg'
    with open(file_output, 'r', encoding='utf-8') as fo:
        content = fo.read()
    lines = content.strip('\n').split('\n')
    content_output = ""
    for line in lines:
        if line[0] == '#':
            content_output += line + '\n'
        else:
            content_output += ','.join(line.split()) + '\n'
    with open(file_output.split('.')[0] + '.csv', 'w', encoding='utf-8') as fo:
        fo.write(content_output)


def main():
    cmds = [i for i in sys.argv]
    file2format = []
    format2 = 0
    for cmd in cmds[1:]:
        if cmd == '-c':
            format2 = 1
        else:
            file2format.append(cmd)
    if format2 == 0:
        for file in file2format:
            format_xvg(file)
    else:
        for file in file2format:
            format_csv(file)
    print("--> ALL DONE ! ")


if __name__ == "__main__":
    main()