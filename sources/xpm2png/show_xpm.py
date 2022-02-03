## author : charlie
## date : 20220130

import os
import argparse
import numpy as np
from scipy.interpolate import interp2d
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt


def readxpm(inputfile: str) -> tuple:
    """read xpm file and return infos"""
    xpm_title, xpm_legend, xpm_type = "", "", ""
    xpm_xlabel, xpm_ylabel = "", ""
    xpm_width, xpm_height = 0, 0
    xpm_color_num, xpm_char_per_pixel = 0, 0
    chars, colors, notes, colors_rgb = [], [], [], []
    xpm_xaxis, xpm_yaxis, xpm_data = [], [], []

    if not os.path.exists(inputfile):
        print("ERROR -> no {} in current directory")
        exit()

    with open(inputfile, "r") as fo:
        lines = [line.strip() for line in fo.readlines()]

    ## parse content of xpm file
    flag_4_code = 0  ## means haven't detected yet
    for line in lines:
        ## finde the 4 code line and parse
        if flag_4_code == 1:  ## means this line is code4 line
            flag_4_code = 2  ## means have detected
            code4 = [int(c) for c in line.strip().strip(",").strip('"').split()]
            xpm_width, xpm_height = code4[0], code4[1]
            xpm_color_num, xpm_char_per_pixel = code4[2], code4[3]
            continue
        elif (flag_4_code == 0) and line.startswith("static char"):
            flag_4_code = 1  ## means next line is code4 line
            continue

        ## parse comments and axis parts
        if line.startswith("/* x-axis"):
            xpm_xaxis += [float(n) for n in line.strip().split()[2:-1]]
            continue
        elif line.startswith("/* y-axis"):
            xpm_yaxis += [float(n) for n in line.strip().split()[2:-1]]
            continue
        elif line.startswith("/* title"):
            xpm_title = line.strip().split('"')[1]
            continue
        elif line.startswith("/* legend"):
            xpm_legend = line.strip().split('"')[1]
            continue
        elif line.startswith("/* x-label"):
            xpm_xlabel = line.strip().split('"')[1]
            continue
        elif line.startswith("/* y-label"):
            xpm_ylabel = line.strip().split('"')[1]
            continue
        elif line.startswith("/* type"):
            xpm_type = line.strip().split('"')[1]
            continue

        items = line.strip().split()
        ## for char-color-note part
        if len(items) == 7 and items[1] == "c":
            if len(items[0].strip('"')) == xpm_char_per_pixel:
                chars.append(items[0].strip('"'))
                colors.append(items[2])
                notes.append(items[5].strip('"'))
            ## deal with blank
            if len(items[0].strip('"')) < xpm_char_per_pixel:
                print("Warning -> space in char of line : {}".format(line))
                char_item = items[0].strip('"')
                chars.append(char_item + " " * (xpm_char_per_pixel - len(char_item)))
                colors.append(items[2])
                notes.append(items[5].strip('"'))
            continue

        ## for content part
        if line.strip().startswith('"') == 1 and (
            len(line.strip().strip(",").strip('"')) == xpm_width * xpm_char_per_pixel
        ):
            xpm_data.append(line.strip().strip(",").strip('"'))

    ## check data
    if len(chars) != len(colors) != len(notes) != xpm_color_num:
        print("Wrong -> length of chars, colors, notes != xpm_color_num")
        print(
            "chars : {}, colors : {}, notes : {}, xpm_color_num : {}".format(
                len(chars), len(colors), len(notes), xpm_color_num
            )
        )
        exit()

    if len(xpm_data) != xpm_height:
        print("ERROR -> rows of data ({}) is not equal to xpm height ({}), check it !".format(len(xpm_data), xpm_height))
        exit()
    if len(xpm_xaxis) != xpm_width and len(xpm_xaxis) != xpm_width + 1:
        print("ERROR -> length of x-axis ({}) != xpm width ({}) or xpm width +1".format(len(xpm_xaxis), xpm_width))
        exit()
    if len(xpm_yaxis) != xpm_height and len(xpm_yaxis) != xpm_height + 1:
        print("ERROR -> length of y-axis ({}) != xpm height ({}) or xpm height +1".format(len(xpm_yaxis), xpm_height))
        exit()

    if len(xpm_xaxis) == xpm_width + 1:
        xpm_xaxis = [
            (xpm_xaxis[i - 1] + xpm_xaxis[i]) / 2.0 for i in range(1, len(xpm_xaxis))
        ]
        print(
            "Warning -> length of x-axis is 1 more than xpm width, use intermediate value for instead. "
        )
    if len(xpm_yaxis) == xpm_height + 1:
        xpm_yaxis = [
            (xpm_yaxis[i - 1] + xpm_yaxis[i]) / 2.0 for i in range(1, len(xpm_yaxis))
        ]
        print(
            "Warning -> length of y-axis is 1 more than xpm height, use intermediate value for instead. "
        )

    ## hex color to rgb values
    for color in colors:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        colors_rgb.append([r, g, b])

    print("Info -> all data has been read from {} successfully.".format(inputfile))

    xpm_infos = (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    )
    return xpm_infos


def drawxpm_origin(xpmfile: str, IP: bool, outputpng: str, noshow: bool) -> None:
    """draw xpm figure"""

    ## check parameters
    if not os.path.exists(xpmfile):
        print("ERROR -> {} not in current directory".format(xpmfile))
        exit()
    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()

    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = readxpm(xpmfile)

    xpm_yaxis.reverse()

    # visualization
    if IP == False:
        img = []
        for line in xpm_data:
            rgb_line = []
            for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
                rgb_line.append(
                    colors_rgb[chars.index(line[i : i + xpm_char_per_pixel])]
                )
            img.append(rgb_line)

        plt.figure()
        plt.imshow(img)

    if IP == True:
        if xpm_type != "Continuous":
            print("ERROR -> Only Continuous type xpm file can interpolation")
            exit()
        ## show figure with interpolation
        imgIP = []
        for line in xpm_data:
            value_line = []
            for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
                value_line.append(
                    float(notes[chars.index(line[i : i + xpm_char_per_pixel])])
                )
            imgIP.append(value_line)

        im = plt.imshow(imgIP, cmap="jet", interpolation="bilinear")
        plt.colorbar(im, fraction=0.046, pad=0.04)

    plt.title(xpm_title)
    plt.xlabel(xpm_xlabel)
    plt.ylabel(xpm_ylabel)
    print("Legend of this xpm figure -> ", xpm_legend)

    # set the ticks
    x_tick, y_tick = 10, 10
    if xpm_width < 100:
        x_tick = int(xpm_width / 3)
    elif xpm_width >= 100 and xpm_width < 1000:
        x_tick = int(xpm_width / 5)
    elif xpm_width > 500:
        x_tick = int(xpm_width / 10)
    if xpm_height < 100:
        y_tick = int(xpm_height / 3)
    elif xpm_height >= 100 and xpm_height < 1000:
        y_tick = int(xpm_height / 5)
    elif xpm_height > 500:
        y_tick = int(xpm_height / 10)
    plt.tick_params(axis="both", which="major")
    x_major_locator = plt.MultipleLocator(x_tick)
    y_major_locator = plt.MultipleLocator(y_tick)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    ax.yaxis.set_major_locator(y_major_locator)
    plt.xticks(
        [w for w in range(1, xpm_width + 1, x_tick)],
        ["{:.2f}".format(xpm_xaxis[i]) for i in range(0, len(xpm_xaxis), x_tick)],
    )
    plt.yticks(
        [h for h in range(1, xpm_height + 1, y_tick)],
        ["{:.2f}".format(xpm_yaxis[i]) for i in range(0, len(xpm_yaxis), y_tick)],
    )

    if outputpng != None:
        plt.savefig(outputpng, dpi=300)
    if noshow == False:
        plt.show()


def drawxpm_newIP(xpmfile: str, IP: bool, outputpng: str, noshow: bool) -> None:
    """draw xpm figure with interpolation by pcolormesh"""

    ## check parameters
    if not os.path.exists(xpmfile):
        print("ERROR -> {} not in current directory".format(xpmfile))
        exit()
    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()

    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = readxpm(xpmfile)

    if xpm_type != "Continuous":
        print("ERROR -> Only Continuous type xpm file can interpolation")
        exit()

    xpm_yaxis.reverse()

    img = []
    for line in xpm_data:
        value_line = []
        for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
            value_line.append(
                float(notes[chars.index(line[i : i + xpm_char_per_pixel])])
            )
        img.append(value_line)

    if IP == False:
        plt.pcolormesh(xpm_xaxis, xpm_yaxis, img, cmap="jet", shading="auto")
    elif IP == True:
        ## interpolation
        ip_func = interp2d(xpm_xaxis, xpm_yaxis, img, kind="linear")
        x_new = np.linspace(np.min(xpm_xaxis), np.max(xpm_xaxis), 10 * len(xpm_xaxis))
        y_new = np.linspace(np.min(xpm_yaxis), np.max(xpm_yaxis), 10 * len(xpm_yaxis))
        value_new = ip_func(x_new, y_new)
        x_new, y_new = np.meshgrid(x_new, y_new)
        ## show figure
        plt.pcolormesh(x_new, y_new, value_new, cmap="jet", shading="auto")

    plt.colorbar()
    plt.title(xpm_title)
    plt.xlabel(xpm_xlabel)
    plt.ylabel(xpm_ylabel)
    print("Legend of this xpm figure -> ", xpm_legend)

    if outputpng != None:
        plt.savefig(outputpng, dpi=300)
    if noshow == False:
        plt.show()


def get_scatter_data(xpm_infos: tuple) -> tuple:
    """convert xpm_infos into scatter data"""
    (
        xpm_title,
        xpm_legend,
        xpm_type,
        xpm_xlabel,
        xpm_ylabel,
        xpm_width,
        xpm_height,
        xpm_color_num,
        xpm_char_per_pixel,
        chars,
        colors,
        notes,
        colors_rgb,
        xpm_xaxis,
        xpm_yaxis,
        xpm_data,
    ) = xpm_infos

    xpm_yaxis.reverse()

    ## parse scatter data
    x, y, v = [], [], []
    scatter_x, scatter_y = [], []
    # print(len(xpm_xaxis))
    # print(len(xpm_yaxis))
    for l in range(len(xpm_data)):
        for i in range(0, xpm_width * xpm_char_per_pixel, xpm_char_per_pixel):
            v.append(float(notes[chars.index(xpm_data[l][i : i + xpm_char_per_pixel])]))
            x.append(xpm_xaxis[int(i / xpm_char_per_pixel)])
            y.append(xpm_yaxis[l])

    v_max = max(v)
    scatter_weight = 1
    for i in range(len(v)):
        count = round((v_max - v[i]) * scatter_weight)
        for _ in range(count):
            scatter_x.append(x[i])
            scatter_y.append(y[i])

    return scatter_x, scatter_y, x, y, v


def extract_scatter(xpms: list) -> None:
    """extract data from xpm and save to csv"""

    for xpm in xpms:
        if not os.path.exists(xpm):
            print("ERROR -> {} not in current directory".format(xpm))
            exit()
        if xpm.split(".")[1] != "xpm":
            print("ERROR -> specify a file with suffix xpm")
            exit()
        outcsv = xpm.split(".")[0] + ".csv"
        if os.path.exists(outcsv):
            print("ERROR -> {} already in current directory".format(outcsv))
            exit()

        xpm_infos = readxpm(xpm)
        if xpm_infos[2] != "Continuous":
            print("ERROR -> can not extract data from xpm whose type is not Continuous")
            exit()

        _, _, x, y, v = get_scatter_data(xpm_infos)
        if len(x) != len(y) != len(v):
            print("ERROR -> wrong in length of x, y, v")
            exit()
        with open(outcsv, "w") as fo:
            fo.write("{},{},{}\n".format("x-axis", "y-axis", "value"))
            for i in range(len(x)):
                fo.write("{:.6f},{:.6f},{:.6f}\n".format(x[i], y[i], v[i]))
        print("Info -> extract data from {} successfully".format(xpm))


def combinexpm(xpm_file_list: list, outputpng: str, noshow: bool) -> None:
    """combine xpm by scatters"""

    x_list, y_list = [], []
    for file in xpm_file_list:
        xpm_infos = readxpm(file)
        if xpm_infos[2] != "Continuous":
            print("ERROR -> can not combine xpm whose type is not Continuous")
            exit()
        x, y, _, _, _ = get_scatter_data(xpm_infos)
        x_list += x
        y_list += y

    ## combine xpm
    # plt.scatter(x_list, y_list)
    # plt.show()

    heatmap, xedges, yedges = np.histogram2d(x_list, y_list, bins=800)
    heatmap = gaussian_filter(heatmap, sigma=16)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    plt.imshow(heatmap.T, origin="lower", extent=extent, cmap="jet_r")
    plt.xlim(extent[0], extent[1])
    plt.ylim(extent[2], extent[3])

    if outputpng != None and os.path.exists(outputpng):
        print("ERROR -> {} already in current directory".format(outputpng))
        exit()
    if outputpng != None:
        plt.savefig(outputpng, dpi=300)
    if noshow == False:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Process xpm files generated by GMX")
    parser.add_argument("-f", "--inputfile", help="input your xpm file")
    parser.add_argument("-o", "--outputpng", help="picture file to output")
    parser.add_argument(
        "-ip",
        "--interpolation",
        action="store_true",
        help="whether to apply interpolation (only support Continuous type xpm)",
    )
    parser.add_argument(
        "-pcm",
        "--pcolormesh",
        action="store_true",
        help="whether to apply pcolormesh function to draw",
    )
    parser.add_argument(
        "-ns",
        "--noshow",
        action="store_true",
        help="whether not to show picture, useful on computer without gui",
    )
    parser.add_argument(
        "-c",
        "--combine",
        nargs="+",
        help="specify some xpm files to combine into one figure",
    )
    parser.add_argument(
        "-e",
        "--extract",
        nargs="+",
        help="specify xpm files to extract scatter data and save to csv file",
    )
    args = parser.parse_args()

    inputxpm = args.inputfile
    outputpng = args.outputpng
    ip = args.interpolation
    noshow = args.noshow
    xpms2combine = args.combine
    pcm = args.pcolormesh
    extract_files = args.extract

    if inputxpm != None and xpms2combine != None:
        print("ERROR -> do not specify -f and -c at once ")
        exit()

    if xpms2combine != None:
        combinexpm(xpms2combine, outputpng, noshow)

    if inputxpm != None:
        if pcm == False:
            drawxpm_origin(inputxpm, ip, outputpng, noshow)
        elif pcm == True:
            drawxpm_newIP(inputxpm, ip, outputpng, noshow)

    if extract_files != None:
        extract_scatter(extract_files)

    print("Good Day !")


if __name__ == "__main__":
    main()
