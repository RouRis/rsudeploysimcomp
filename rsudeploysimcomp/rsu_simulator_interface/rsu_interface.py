import pandas as pd


class RSU_SIM_Interface:
    def export_picked_locations_to_csv(self, file_path, junctions):
        data = list(junctions)
        agent_ids = [200000 + i for i in range(len(junctions))]
        time_steps = [0] * len(junctions)
        df = pd.DataFrame({
            "time_step": time_steps,
            "agent_id": agent_ids,
            "x": [coord[0] for coord in data],
            "y": [coord[1] for coord in data]
        })
        df.to_csv(file_path, index=False)

    def convert_csv_to_parquet(self, csv_file_path, parquet_file_path):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        # Convert the DataFrame to Parquet format
        df.to_parquet(parquet_file_path, index=False)