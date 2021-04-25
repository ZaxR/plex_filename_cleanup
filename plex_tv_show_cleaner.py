import ast
import os
import re


def make_uppercase(episode):
    return episode.upper()


def convert_bracket_x_fmt(episode):
    return episode.replace("[", "S").replace("x", "E").replace("]", "").upper()


EPISODE_CLEANUP = [
    {"episode_fmt": "(S[0-9]+E[0-9]+)", "clean_fmt": make_uppercase},
    {"episode_fmt": "(\[[0-9]+x[0-9]+-?[0-9]*?\])", "clean_fmt": convert_bracket_x_fmt},
    # {"episode_fmt": "(\s+[0-9]{3, 4}\s+)", "clean_fmt": f"{S}{episode[0]}{E}{episode[1:]}"},
    # S+E as one number -or- episode number from beginning of series
]

JUNK_SEPS = [
    "hdtv",
    "web",
    "rerip",
    "480p",
    "720p",
    "1080p",
]


def infer_show_name(path):
    """ Attempt to find the show name from the parent or grandparent folder name.

    Assumes episodes are organized into folders by show
    and optionally subdivided by season.

    """
    try:
        path_parts = path.rsplit("/")
        if "season" in path_parts[-1].lower():
            return path_parts[-2]
        return path_parts[-1]
    except IndexError:
        return show_name


def get_clean_show_name(show_name):
    # word_seps = [".", "-"]
    show_name_words = show_name.replace(".", " ").replace("-", " ").strip().split(" ")
    return " ".join([w.title() for w in show_name_words if w != ""])


def get_clean_episode_title(extra):
    clean_episode_title = ""
    for sep in JUNK_SEPS:
        sep_idx = extra.lower().find(sep.lower())
        if sep_idx != -1:
            valid_clean_episode = True
            clean_episode_title = extra[:sep_idx].replace(".", " ").replace("-", " ").strip()
            break

    return clean_episode_title


def clean_tv_episodes(walk_dir="."):
    for root, dirs, file_names in os.walk(walk_dir):
        # TODO Clean season folder titles to not include show name
        for file_name in file_names:
            valid_fmt_found = False
            for fmt in EPISODE_CLEANUP:
                try:
                    show_name, episode, extra = re.split(fmt["episode_fmt"], file_name, maxsplit=1, flags=re.I)
                    clean_episode = fmt["clean_fmt"](episode)
                    valid_fmt_found = True
                    break
                except ValueError:
                    pass
            if valid_fmt_found == False:
                print(f"{file_name} doesn't match cleanup pattern. No renaming being done.")
                continue

            if show_name == "":
                show_name = infer_show_name(path=root)
            clean_show_name = get_clean_show_name(show_name)
            clean_episode_title = get_clean_episode_title(extra)
            ext = extra.rsplit(".", 1)[1].strip()

            clean_file_name = (
                f"{clean_show_name} - {clean_episode} - {clean_episode_title}.{ext}"
                if clean_episode_title else
                f"{clean_show_name} - {clean_episode}.{ext}"
            )

            os.rename(f"{root}/{file_name}", f"{root}/{clean_file_name}")


if __name__ == "__main__":
    clean_tv_episodes()
