import click
import ffmpeg
import os
import sys
import math

# data for .spec file
# ('iphone/*.png', 'iphone'),
# ('ipad/*.png', 'ipad'),
# ('mac/*.png', 'mac')


def p(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("src")

    return os.path.join(base_path, relative_path)


def setup(device, island, background):
    if device == "iPhone-16-Pro":
        CONTENT_SIZE = [884, 1918]
        mask_path = p("iphone/mask_iPhone-16-pro.png")
        if island:
            if background:
                frame_path = p("iphone/frame_iPhone-16-pro-island-background.png")
            else:
                frame_path = p("iphone/frame_iPhone-16-pro-island.png")
        else:
            if background:
                frame_path = p("iphone/frame_iPhone-16-pro-background.png")
            else:
                frame_path = p("iphone/frame_iPhone-16-pro.png")
    elif device == "iPad-11-Pro":
        CONTENT_SIZE = [1310, 1898]
        mask_path = p("ipad/mask_iPad-11-pro.png")
        if background:
            frame_path = p("ipad/frame_iPad-11-pro-background.png")
        else:
            frame_path = p("ipad/frame_iPad-11-pro.png")
    elif device == "macbook-pro-14":
        CONTENT_SIZE = [2504, 1628]
        mask_path = p("mac/mask_macbook-pro-14.png")
        if background:
            frame_path = p("mac/frame_macbook-pro-14-background.png")
        else:
            frame_path = p("mac/frame_macbook-pro-14.png")
    return (CONTENT_SIZE, frame_path, mask_path)


def calculate_size(current, target):
    factor_horizontal = target[0] / current[0]
    factor_vertical = target[1] / current[1]
    factor = max(factor_horizontal, factor_vertical)
    return [round(dim * factor) for dim in current]


def generate(
    file_path,
    output_path,
    CONTENT_SIZE,
    frame_path,
    mask_path,
    resolution_h,
    background,
    codec,
):

    # load inputs
    original = ffmpeg.input(file_path)
    mask = ffmpeg.input(mask_path)
    frame = ffmpeg.input(frame_path)

    # probe original to precompute dimensions
    probe = ffmpeg.probe(file_path)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    original_size = [video_stream["width"], video_stream["height"]]

    # probe frame to precompute frame_path
    probe = ffmpeg.probe(frame_path)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    frame_size = [video_stream["width"], video_stream["height"]]

    # overwrite width in case of background
    if background:
        resolution_h = 1000
    if resolution_h == -1:
        # default resolution_h is half of framewidth
        resolution_h = frame_size[0] // 2

    # update mask
    mask = mask.filter("scale", resolution_h, -1).filter(
        "pad", "ceil(iw/2)*2", "ceil(ih/2)*2"
    )

    # compute target size
    [width, height] = calculate_size(original_size, CONTENT_SIZE)
    original = (
        ffmpeg.filter(original, "scale", width, height)
        .filter(
            "crop",
            CONTENT_SIZE[0],
            CONTENT_SIZE[1],
            (width - CONTENT_SIZE[0]) // 2,
            (height - CONTENT_SIZE[1]) // 2,
        )
        .filter(
            "pad",
            frame_size[0],
            frame_size[1],
            (frame_size[0] - CONTENT_SIZE[0]) / 2,
            (frame_size[1] - CONTENT_SIZE[1]) / 2,
        )
        .filter("scale", resolution_h, -1)
        .filter("pad", "ceil(iw/2)*2", "ceil(ih/2)*2")
    )

    (
        ffmpeg.filter([original, mask], "alphamerge")
        .overlay(
            frame.filter("scale", resolution_h, -1).filter(
                "pad", "ceil(iw/2)*2", "ceil(ih/2)*2"
            )
        )
        .output(output_path, vcodec=codec)
        .overwrite_output()
        .run()
    )


@click.command()
@click.argument("input_path", type=click.Path())
@click.option(
    "-i",
    "--island",
    is_flag=True,
    default=False,
    help="Adds a dynamic island. Use this if the screen recording does not include the notch / dynamic island. Default: --no-island.",
)
@click.option(
    "-b",
    "--background",
    is_flag=True,
    default=False,
    help="Adds a white background to reduce the file size.",
)
@click.option(
    "-w",
    "--width",
    type=int,
    default=-1,
    help="The horizontal resolution of the output. Is ignored when background flag is set.",
)
@click.option(
    "--device",
    required=True,
    type=click.Choice(
        ["iPhone-16-Pro", "iPad-11-Pro", "macbook-pro-14"], case_sensitive=False
    ),
    help="Device used for the frame and aspect ratio. Default: iPhone-16-Pro.",
    default="iPhone-16-Pro",
)
def main(device, input_path, island, width, background):
    """
    INPUT_PATH is the path to the raw file e.g. a screen recording or a directory. \n
    """

    # set content size and frame according to chosen device
    (CONTENT_SIZE, frame_path, mask_path) = setup(device, island, background)

    # set codec
    if background:
        codec = "libx264"
    else:
        codec = "prores_ks"

    if os.path.isfile(input_path):
        output_path = os.path.splitext(input_path)[0] + "_output.mov"
        generate(
            input_path,
            output_path,
            CONTENT_SIZE,
            frame_path,
            mask_path,
            width,
            background,
            codec,
        )
    elif os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            if not filename.lower().endswith((".mp4", ".mov", ".avi")):
                continue
            if os.path.splitext(filename)[0].endswith("_output"):
                continue
            file_path = os.path.join(input_path, filename)
            output_path = os.path.splitext(file_path)[0] + "_output.mov"
            generate(
                file_path,
                output_path,
                CONTENT_SIZE,
                frame_path,
                mask_path,
                width,
                background,
                codec,
            )
    else:
        click.echo("Invalid input. Provide a valid file or directory.")


if __name__ == "__main__":
    main()
