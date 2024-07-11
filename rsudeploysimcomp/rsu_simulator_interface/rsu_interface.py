import pandas as pd


class RSU_SIM_Interface:
    def export_picked_locations_to_csv(self, file_path, junctions):
        data = list(junctions)
        df = pd.DataFrame(data, columns=["x", "y"])
        df.to_csv(file_path, index=False)
