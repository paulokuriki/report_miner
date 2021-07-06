import PySimpleGUI as sg


def main_screen(filter_set):
    sg.theme('DarkBlue')
    bold = ("Arial", 10, "bold")

    file_list_column = [
        [
            sg.Text("CSV Dataset", font=bold),
            sg.InputText(size=(45, 1), enable_events=True, key="-CSV FILENAME-"),
            sg.FilesBrowse(file_types=(("CSV Files", "*.csv"),), key="-OPEN CSV FILE-"),
            sg.Checkbox("Remove SW", default=False, key="-STOPWORDS-",
                        tooltip="Remove StopWords. This process can take some time.")
        ],
        [
            sg.Text("Select Filter", font=bold),
            sg.Combo(values=filter_set, size=(43, 1), key="-COMBO FILTER-"),
            sg.Button("Load Filter", key="-LOAD FILTER-"),
            sg.Button("Delete Filter", key="-DELETE FILTER-"),
        ],
        [sg.Text("Inclusion Words", font=bold)],
        [sg.Multiline(s="", size=(80, 10), key="-INCLUSION-")],
        [sg.Text("Exclusion Words", font=bold)],
        [sg.Multiline(s="", size=(80, 35), key="-EXCLUSION-")],
        [sg.Button("Process", key="-PROCESS-"),
         sg.Button("Save Filter  Words", key="-SAVE FILTER-")
         ],
    ]

    results = [
        [sg.Text("RESULTS", font=bold)],
        [sg.Multiline(s="", size=(120, 51), key="-RESULTS-")],
        [
            sg.Text("Export to CSV:", font=bold),
            sg.In(size=(92, 1), enable_events=True, key="-EXPORT FILENAME-"),
            sg.FilesBrowse("Browse", file_types=(("CSV Files", "*.csv"),)),
            sg.Button("Save", key="-EXPORT CSV-"),
        ]
    ]

    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(results),
        ]
    ]

    return layout
