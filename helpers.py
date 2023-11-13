import string


def clean_filename(title):
    title = title.lower()
    title = title.translate(str.maketrans("", "", string.punctuation))
    title = title.replace(" ", "_")
    return title


def time_to_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.replace(",", ".").split(":"))
    return hours * 3600 + minutes * 60 + seconds


def get_caption_at_time(captions, played_seconds):
    for caption in captions:
        start_time, end_time = caption["start"], caption["end"]
        start_seconds, end_seconds = time_to_seconds(start_time), time_to_seconds(
            end_time
        )
        if start_seconds <= played_seconds <= end_seconds:
            return caption["text"]
    return ""


def parse_srt(srt_text):
    captions = []
    lines = srt_text.strip().split("\n\n")
    for line in lines:
        parts = line.split("\n")
        if len(parts) >= 3:
            index = parts[0]
            time_range = parts[1].split(" --> ")
            if len(time_range) == 2:
                start_time = time_range[0]
                end_time = time_range[1]
                text = "\n".join(parts[2:])
                captions.append(
                    {
                        "index": index,
                        "start": start_time,
                        "end": end_time,
                        "text": text,
                    }
                )
    return captions


def parse_webvtt(webvtt_text):
    captions = []
    lines = webvtt_text.strip().split("\n")

    # Skip the header lines
    lines = lines[4:]

    for line in lines:
        time_range = line.split(" --> ")
        if len(time_range) == 2:
            start_time = time_range[0]
            end_time = time_range[1]
            text = lines[lines.index(line) + 1]
            captions.append(
                {
                    "start": start_time,
                    "end": end_time,
                    "text": text,
                }
            )
    return captions
