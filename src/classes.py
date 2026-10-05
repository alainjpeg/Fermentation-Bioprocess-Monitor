import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims): #utility class
        self.df = pd.read_csv(filepath)
        self.ph_lims = ph_lims
        self.temperature_lims = temperature_lims
    def extract_batch(self, batch_id): #extracts data, returns panda.DataFrame
        df_batch = self.df[self.df["batch_id"] == batch_id]
        return df_batch

    def optimal_ph_mask(self, df_batch): #determine if ph is good
        mask = df_batch["pH"].between(self.ph_lims[0], self.ph_lims[1])
        return mask

    def optimal_temperature_mask(self, df_batch): #determine if temp is good
        mask = df_batch["temperature_C"].between(
            self.temperature_lims[0],
            self.temperature_lims[1]
        )

        return mask

    def get_n_batches(self): #get number of batches
        n_batches = self.df["batch_id"].nunique()
        return n_batches

    def export_dashboard(self, batch_id, filepath): #create and extract dashboard
        df_batch = self.extract_batch(batch_id)
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes[0, 0].scatter( #scatter plot
            df_batch["time_h"],
            df_batch["C_glucose_g_L^-1"],
            label="glucose", #label name
            marker="o" #marker shape
        )
        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_biomass_g_L^-1"],
            label="biomass",
            marker="^"
        )
        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_product_g_L^-1"],
            label="product",
            marker="s" #s = square
        )
        axes[0,0].set_xlabel("Time [h]")
        axes[0, 0].set_ylabel("Concentration [g/L]")
        axes[0, 0].legend()
        temperature_mask = self.optimal_temperature_mask(df_batch) #which temp optimal

        axes[0, 1].scatter( #optimal temp graph
            df_batch.loc[temperature_mask, "time_h"],
            df_batch.loc[temperature_mask, "temperature_C"],
            color='green', label="optimal", marker="o", #Can all be done on one line
        )
        axes[0, 1].scatter( #suboptimal temp graph
            df_batch.loc[~temperature_mask, "time_h"],
            df_batch.loc[~temperature_mask, "temperature_C"],
            color='red', label="Sub-Optimal", marker="x",
        )
        axes[0, 1].set_xlabel("Time [h]")
        axes[0, 1].set_ylabel("Temperature [°C]")
        axes[0, 1].legend()
        ph_mask = self.optimal_ph_mask(df_batch)

        axes[1, 0].scatter(  # optimal ph graph
            df_batch.loc[ph_mask, "time_h"],
            df_batch.loc[ph_mask, "pH"],
            color='green', label="optimal", marker="o"
        )
        axes[1, 0].scatter(  # optimal ph graph
            df_batch.loc[~ph_mask, "time_h"],
            df_batch.loc[~ph_mask, "pH"],
            color='red',  label="Sub-Optimal", marker="x"
        )
        axes[1, 0].set_xlabel("Time [h]")
        axes[1, 0].set_ylabel("pH")
        axes[1, 0].legend()

        axes[1,1].scatter(
            df_batch["time_h"],
            df_batch["DO_percent"],
            marker='o'
        )
        axes[1,1].set_xlabel("Time [h]")
        axes[1,1].set_ylabel("Dissolved Oxygen (DO) [%]")

        #6h spacing
        for ax in axes.flat:
            ax.xaxis.set_major_locator(MultipleLocator(6)) #where 6 is hrs of spacing

        #save and close
        fig.tight_layout()
        fig.savefig(filepath)
        plt.close(fig)
    def export_summary(self, filepath): #batch summary table to csv
        summary_data=[] #list
        for batch_id in range(1, self.get_n_batches()+1): #for all batches
            df_batch = self.extract_batch(batch_id) #extract
            ph_mask = self.optimal_ph_mask(df_batch) #determine optimal ph
            temperature_mask = self.optimal_temperature_mask(df_batch) #determine optimal temp
            ph_optimal_percent = round(ph_mask.mean() * 100, 2) #calc %PH optimal
            temperature_optimal_percent = round(temperature_mask.mean() * 100, 2) #calc %temp optimal
            final_product = df_batch["C_product_g_L^-1"].iloc[-1] #final product conc
            summary_data.append({ #temp save
                "batch_id": batch_id,
                "ph_optimal_percent": ph_optimal_percent,
                "temperature_optimal_percent": temperature_optimal_percent,
                "C_product_g_L^-1_final": final_product
            })
        df_summary = pd.DataFrame(summary_data) #summarize
        df_summary.to_csv(filepath, index=False) #export as csv

