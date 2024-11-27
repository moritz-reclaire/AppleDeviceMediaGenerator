import click
import ffmpeg
import os
import sys

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


def setup(device, island):
    if device == "iPhone-16-Pro":
        CONTENT_SIZE = [884, 1918]
        mask_path = p("iphone/mask_iPhone-16-pro.png")
        if island:
            frame_path = p("iphone/frame_iPhone-16-pro-island.png")
        else:
            frame_path = p("iphone/frame_iPhone-16-pro.png")
    elif device == "iPad-11-Pro":
        CONTENT_SIZE = [1310, 1898]
        frame_path = p("ipad/frame_iPad-11-pro.png")
        mask_path = p("ipad/mask_iPad-11-pro.png")
    elif device == "macbook-pro-14":
        CONTENT_SIZE = [2504, 1628]
        frame_path = p("mac/frame_macbook-pro-14.png")
        mask_path = p("mac/mask_macbook-pro-14.png")
    return (CONTENT_SIZE, frame_path, mask_path)


def calculate_size(current, target):
    factor_horizontal = target[0] / current[0]
    factor_vertical = target[1] / current[1]
    factor = max(factor_horizontal, factor_vertical)
    return [round(dim * factor) for dim in current]


@click.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_path", type=click.Path(dir_okay=False))
@click.option(
    "--island/--no-island",
    default=False,
    help="Adds a dynamic island. Use this if the screen recording does not include the notch / dynamic island. Default: --no-island.",
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
def generate(device, input_path, output_path, island):
    """
    INPUT_PATH is the path to the raw file e.g. a screen recording. \n
    OUTPUT_PATH is the path to the produced file.
    """

    # set content size and frame according to chosen device
    (CONTENT_SIZE, frame_path, mask_path) = setup(device, island)

    # load inputs
    original = ffmpeg.input(input_path)
    mask = ffmpeg.input(mask_path)
    frame = ffmpeg.input(frame_path)

    # probe original to precompute dimensions
    probe = ffmpeg.probe(input_path)
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
    )

    (
        ffmpeg.filter([original, mask], "alphamerge")
        .overlay(frame)
        .output(
            output_path,
            vcodec="prores_ks",
        )
        .overwrite_output()
        .run()
    )


if __name__ == "__main__":
    generate()
