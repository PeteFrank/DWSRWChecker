import json
from decodetxt2rw import get_filename_list, RW_JSON_FOLDER
from decodexls2wz import WZ_JSON_FOLDER


OUTPUT_FOLDER = "compare_result/"

class CompareSet():

    def __init__(self, wz_list: list, rw_list: list, wz_data: dict, rw_data: dict) -> None:
        self.compose_wz_dict(wz_list, wz_data)
        self.compose_rw_dict(rw_list, rw_data)
    

    def compose_wz_dict(self, wz_list: list, wz_data: dict) -> None:
        self.wz_list = wz_list
        self.wz_dict = dict()
        self.wz_dict["WZ_numbers"] = []
        self.wz_dict["DWS_numbers"] = []
        self.wz_dict["items"] = dict()
        for wz in self.wz_list:
            try:    
                self.wz_dict["WZ_numbers"].append(wz)
                self.wz_dict["DWS_numbers"].append(wz_data[wz]["DWS_number"])
                for item in wz_data[wz]["items"]:
                    self.wz_dict["items"][item["index"]] = self.wz_dict["items"].get(item["index"], {})
                    self.wz_dict["items"][item["index"]]["name"] = item["name"]
                    self.wz_dict["items"][item["index"]]["quantity"] = self.wz_dict["items"][item["index"]].get("quantity",0) + item["quantity"]
            except KeyError:
                self.wz_dict["WZ_numbers"].remove(wz)
                self.wz_dict["WZ_numbers"].append("Nie znaleziono WZ: "+wz)


    def compose_rw_dict(self, rw_list: list, rw_data: dict) -> None:
        self.rw_list = rw_list
        self.rw_dict = dict()
        self.rw_dict["RW_numbers"] = []
        self.rw_dict["items"] = dict()
        for rw in self.rw_list:
            self.rw_dict["RW_numbers"].append(rw)
            for item in rw_data[rw]["items"]:
                self.rw_dict["items"][item["index"]] = self.rw_dict["items"].get(item["index"], int(0)) + item["quantity"]


    def compare(self) -> str:
        self.comparision_result = "{:*<150}\n".format("")
        self.comparision_result += ("WZ-ty  : " + str(self.wz_list) + "\n")
        self.comparision_result += ("DWSygn : " + str(self.wz_dict["DWS_numbers"]) + "\n")
        self.comparision_result += ("RW     : " + str(self.rw_list) + "\n")
        self.comparision_result += "{:-<150}\n".format("")
        self.comparision_result += " STATUS   INDEX   ILOŚĆ (WZ)  ILOŚĆ (RW)  NAZWA TOWARU\n"
        self.comparision_result += "{:-<150}\n".format("")
        indexes = set(list(self.wz_dict["items"].keys()) + list(self.rw_dict["items"].keys()))
        for i in indexes:
            try:
                rw_quantity = self.rw_dict["items"].get(i,0)
                wz_quantity = self.wz_dict["items"][i]["quantity"]
                if wz_quantity == rw_quantity:
                    status = "OK"
                else:
                    status = "RÓŻNICA"
                name = self.wz_dict["items"][i]["name"]
            except KeyError:
                status = "RÓŻNICA"
                wz_quantity = 0
                name = ""   
            self.comparision_result += "{0:^7}  {1:>6}   {2:>10}  {3:>10}  {4}\n".format(
                status, i, wz_quantity, rw_quantity, name
            )
        self.comparision_result += "{:-<150}\n{:*<150}\n\n".format("","")
        return self.comparision_result


    def get_wz_dict(self) -> dict:   
        return self.wz_dict


    def get_rw_dict(self) -> dict:
        return self.rw_dict


    def __str__(self) -> str:
        return json.dumps([self.wz_dict, self.rw_dict], indent=2)


class RWComparator():
    
    def __init__(self, wz_filenames: list, rw_filenames: list) -> None:
        self.wz_filenames = wz_filenames
        self.rw_filenames = rw_filenames
    

    def load_rw_data(self):
        self.rw_data = {}
        for fn in self.rw_filenames:
            item = load_json(fn)
            self.rw_data[item.get("RW_document","Rw/unknown")] = {"DWS_documents" : item.get("DWS_documents",[]),
                                                                "WZ_documents" : item.get("WZ_documents", []), 
                                                                "items" : item.get("items",[])
            }
        

    def load_wz_data(self):
        self.wz_data = {}
        for fn in self.wz_filenames:
            item = load_json(fn)
            self.wz_data[item.get("WZ_number","000/00")] = {"DWS_number": item.get("DWS_number",[]), "items" : item.get("items",[])}


    def generate_WZ_references(self) -> None:
        self.wz_references = {key: {"checked": False, "items": set()} for key in self.wz_data.keys()} 
        for rw_key, wz_items in self.rw_data.items():
            for wz_num in wz_items["WZ_documents"]:
                if self.wz_references.get(wz_num, None):
                    self.wz_references[wz_num]["items"].add(rw_key)
                else:
                    self.wz_references[wz_num] = {"checked": False, "items": set([rw_key])}


    def generate_RW_references(self) -> None:
        self.rw_references = {key: {"checked": False, "items": set()} for key in self.rw_data.keys()}
        for rw_key, wz_items in self.rw_data.items():
            for rw_num in wz_items["WZ_documents"]:
                self.rw_references[rw_key]["items"].add(rw_num)


    def get_dependencies(self):
        self.generate_RW_references()
        self.generate_WZ_references()
        self.references = [self.__aggregate_indexes__(wz) for wz in self.wz_references if not self.wz_references[wz]["checked"]]


    def __aggregate_indexes__(self, wz_num: str) -> list:
        result_WZ_list = [wz_num]
        self.wz_references[wz_num]["checked"] = True
        tmp_RW_set = {rw for rw in self.wz_references[wz_num]["items"] if not self.rw_references[rw]["checked"]}
        result_RW_list = list(tmp_RW_set)
        for rw in tmp_RW_set:
            self.rw_references[rw]["checked"] = True
            tmp_WZ_set = {wz for wz in self.rw_references[rw]["items"] if not self.wz_references[wz]["checked"]}
            for wz in tmp_WZ_set:
                [wz_res, rw_res] = self.__aggregate_indexes__(wz)
                for o_wz in wz_res:
                    result_WZ_list.append(o_wz)
                for o_rw in rw_res:
                    result_RW_list.append(o_rw)
        return [result_WZ_list, result_RW_list]


    @classmethod
    def load_json(filename: str) -> dict:
        try:
            with open(filename, "r", encoding="UTF-8") as stream:
                output = json.load(stream)
        except:
            output = {}
        return output


    def print_references(self) -> None:
        for ref in self.references:
            print(f"Wz: {ref[0]}\nRw: {ref[1]}\n")


    def print_wz_references(self) -> None:
        for k, v in self.wz_references.items():
            print(f"Wz: {k} checked: {v['checked']}")
    

    def print_rw_references(self) -> None:
        for k, v in self.rw_references.items():
            print(f"{k} checked: {v['checked']}")




def load_json(filename: str) -> dict:
    try:
        with open(filename, "r", encoding="UTF-8") as stream:
            output = json.load(stream)
    except:
        output = {}
    return output


def get_global_wz_data(wz_files: list) -> dict:
    result = {}
    for fn in wz_files:
        item = load_json(fn)
        result[item["WZ_number"]] = {"DWS_number": item["DWS_number"], "items" : item["items"]}
    return result


def get_global_rw_data(rw_files: list) -> dict:
    result = {}
    for fn in rw_files:
        item = load_json(fn)
        result[item["RW_document"]] = {"DWS_documents" : item["DWS_documents"], "WZ_documents" : item["WZ_documents"], "items" : item["items"]}
    return result


def get_RW_to_WZ_reference(rw_data: dict, wz_data: dict) -> dict:
    wz_dict = {key: {"checked": False, "items": set()} for key in wz_data.keys()} 
    for k, v in rw_data.items():
        for wz_num in v["WZ_documents"]:
            wz_dict[wz_num]["items"].add(k)
    return wz_dict


def get_WZ_to_RW_reference(rw_data: dict, wz_data: dict) -> dict:
    rw_dict = {key: {"checked": False, "items": set()} for key in rw_data.keys()}
    for k, v in rw_data.items():
        for rw_num in v["WZ_documents"]:
            rw_dict[k]["items"].add(rw_num)
    return rw_dict


def main():
    rw_json_list = get_filename_list(RW_JSON_FOLDER, "*.json")
    wz_json_list = get_filename_list(WZ_JSON_FOLDER, "*.json")

    comparator = RWComparator(wz_json_list,rw_json_list)
    comparator.load_rw_data()
    comparator.load_wz_data()
    comparator.get_dependencies()
    # comparator.print_references()
    # comparator.print_rw_references()
    # comparator.print_wz_references()

    comp = [CompareSet(ref[0], ref[1], comparator.wz_data, comparator.rw_data) for ref in comparator.references]
    for c in comp:
        print(c.compare())
    # wz_data = get_global_wz_data(wz_json_list)
    # rw_data = get_global_rw_data(rw_json_list)
    # wz_index = get_RW_to_WZ_reference(rw_data, wz_data)
    # rw_index = get_WZ_to_RW_reference(rw_data,wz_data)
    # for k,v in wz_index.items():
    #     print(k, ":",v)
    # json_wzts = json.dumps(wz_data, indent=3)
    # print(json_wzts)
    # obj = load_json(wz_json_list[0])
    # print(obj["WZ_number"])
    # json_formatted = json.dumps(obj, indent=2)
    # print(json_formatted)




if __name__ == "__main__":
    main()