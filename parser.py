import requests
"""                         2                 1
⦁	Température (Sensor 62182233 et sensor 06182660)
                        2
⦁	Humidité (sensor 62182233)
⦁	Niveau batterie (Sensor 62182233 et sensor 06182660)
                            2
⦁	Signal RSSI (Sensor 62182233 et sensor 06182660)
⦁	La date et heure du relevé
"""

capteurs = ["06182660", "62182233", "06190484"]

parsed = [
    {"name": "start_symbol", "length": 2},
    {"name": "packet_length", "length": 2},
    {"name": "protocol_type", "length": 2},
    {"name": "hardware_type", "length": 2},
    {"name": "firmware_version", "length": 4},
    {"name": "IMEI", "length": 8},
    {"name": "RTC_time", "length": 6},
    {"name": "reserved", "length": 2},
    {"name": "state_data_length", "length": 2},
    {"name": "alarm_type", "length": 1},
    {"name": "terminal_information", "length": 1},
    {"name": "reserved", "length": 2},
    {"name": "battery_voltage", "length": 2},
    {"name": "power_voltage", "length": 2},
    {"name": "TAG_information_data", "length": 2},
    {"name": "TAG_type", "length": 1},
    {"name": "number_of_tag", "length": 1, },
    {"name": "length_of_per_TAG", "length": 1},
    {"name": "TAG_information", "length": 11},
    {"name": "packet_index", "length": 2},
    {"name": "check_code", "length": 2},
    {"name": "stop_symbol", "length": 2}
]

toHex = ["start_symbol", "packet_length", "protocol_type"]


def takeIndex(e):
    return int(e["index"])


class miniParser:
    def __init__(self, string, date, verbose=False):
        self.string = string
        self.date = date
        self.verbose = verbose
        self.capteurs = self.findCpInfos()
        print(f"liste de capteurs {self.capteurs}")
        if self.verbose:
            print(f"\n string returned {self.string} \n")

    def findCpInfos(self):
        if self.verbose:
            print("findCpInfos... \n")

        myData = []
        listIndices = []
        returned = []

        for index, i in enumerate(capteurs):
            string_to_parse = self.string
            f = self.string.find(i)
            if f != -1 and f != 1:
                listIndices.append({"name": index + 1, "index": f})

            if self.verbose:
                print(f"capteur {index + 1} index {f} \n")
        listIndices.sort(key=takeIndex)
        print(f"check sorting {listIndices} \n")

        for indice in reversed(listIndices):
            print(indice)
            current_string = self.string[int(indice["index"]) + 8:]
            if self.verbose:
                print(f' current capteur {indice["name"]} current string {current_string} \n')
                print(f' current capteur {indice["name"]} current index {indice["index"]} \n')
                print("\n")
                print(f' old self string {self.string} \n ')
            self.string = self.string[:int(indice["index"])]
            if self.verbose:
                print(f' new self string {self.string} \n')
                print(f' length of the capteur string {len(current_string)} \n')
            myData.append({'capteur': f'{indice["name"]}', 'string': f'{current_string}'})
        if self.verbose:
            print("MYDATA \n")
            print(myData)

        for data in myData:
            if self.verbose:
                print("show data \n")
                print("data " + str(data))

            c = self.capteurParse(data['string'], data["capteur"])
            returned.append(c)
            if self.verbose:
                print(f" checking capteur {c}")

        if self.verbose:
            print(f" self string brought back {self.string}")

        if len(self.string) > 0:
            print(f"reste du string : {self.string}")
        if self.verbose:
            print("\n")
            print("MYDATA \n")
            print(myData)
        return returned

    def capteurParse(self, string, capteur):
        if (len(string) > 17):
            temperature = string[14:18]
            print("TEMPERATURE \n")
            print(temperature)
            print(temperature[2:4])
            h = int(temperature[2:4], base=16)

            temp2 = {"température": h / 10}
            h = int(temperature[0:2], base=16)

            pol = '{0:08b}'.format(h)

            if int(pol[1]) == int(0):
                if self.verbose:
                    print("positive")
                temp2["polarité"] = "positive"
            else:
                print("negative")
                temp2["polarité"] = "negative"

            if int(pol[0]) == int(0):
                if self.verbose:
                    print("normal")
                temp2["norme"] = "normal"
            else:
                if self.verbose:
                    print("abnormal")
                temp2["norme"] = "abnormal"

            humidity = 0
            if string[18:20] == "FF":
                humidity = 0
            else:
                humidity = int(string[18:20], base=16)
            temp = {"capteur": capteur,
                    "ID": string[0:8],
                    "status": string[8:10],
                    "battery_voltage": int(string[10:14], base=16) * 0.001,
                    "temperature": temp2,
                    "humidity": humidity,
                    "RSSI": string[20:22]}
            return temp
        else:
            return {}

    def parser(self, parse_element):

        if len(self.string[0:int(parse_element["length"]) * 2]) > 1:
            # print(f'{parse_element["name"]} :  {self.string[0:int(parse_element["length"])*2]}')
            temp = {parse_element["name"]: self.string[0:int(parse_element["length"]) * 2]}
            if self.verbose:
                print(temp)

            if parse_element["name"] in toHex:

                temp["meaning"] = int(temp[parse_element["name"]], base=16)
            elif parse_element["name"] == "RTC_time":

                temp["meaning"] = self.date



            elif parse_element["name"] == "TAG_information":
                if self.verbose:
                    print("parsing TAG information")
                temperature = temp[parse_element["name"]][14:18]
                if self.verbose:
                    print(f"température {temperature}")
                h = int(temperature[2:4], base=16)

                temp2 = {"température": h}
                h = int(temperature[0:2], base=16)

                pol = '{0:08b}'.format(h)

                if int(pol[1]) == int(0):
                    if self.verbose:
                        print("positive")
                    temp2["polarité"] = "positive"
                else:
                    print("negative")
                    temp2["polarité"] = "negative"

                if int(pol[0]) == int(0):
                    if self.verbose:
                        print("normal")
                    temp2["norme"] = "normal"
                else:
                    if self.verbose:
                        print("abnormal")
                    temp2["norme"] = "abnormal"

                humidity = 0
                if temp[parse_element["name"]][18:20] == "FF":
                    humidity = 0
                else:
                    humidity = int(temp[parse_element["name"]][18:20], base=16)

                temp = {**temp, "ID": temp[parse_element["name"]][0:8], "status": temp[parse_element["name"]][8:10],
                        "battery_voltage": int(temp[parse_element["name"]][10:14], base=16) * 0.001,
                        "temperature": temp2,
                        "humidity": humidity,
                        "RSSI": -int(temp[parse_element["name"]][20:], base=16)}

            self.string = self.string[int(parse_element["length"]) * 2:]
            return temp
        else:
            return {"none": "none"}


class ListCapteur:
    def __init__(self):
        r = requests.get("http://app.objco.com:8099/?account=MRHAOCUYL2&limit=6")
        print(r.status_code)
        print(r.json())
        response = r.json()
        self.response = response
        self.liste = []
        for cp in response:
            wifi_data = cp[1]
            d = cp[2]
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            u = [index + 1 for index, m in enumerate(months) if m == (d[8:11])][0]
            if u < 10:
                u = "0" + str(u)

            date = f"{d[5:7]}/{u}/{d[12:16]} à {d[17:19]}:{d[20:22]}:{d[23:25]}"

            parser = miniParser(wifi_data, date)
            r = []

            for i in parsed:
                temp = parser.parser(i)
                r.append(temp)
            self.liste.append(r)
            print("\n")
            print(parser.string)
            print("\n")
            # print(f" end of parsing ... rest: {parser.string}")

    def get(self):
        return self.liste

    def show(self):
        for index, i in enumerate(self.liste):
            print(f"capteur {index + 1} :")
            print(i)



li = ListCapteur()
li.show()