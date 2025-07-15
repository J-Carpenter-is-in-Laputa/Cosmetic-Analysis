import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime

class CosmeticsAnalyzer:
    def __init__(self, data_path):
        # ^---runs the class to work with the datset
        self.data_path = data_path
        self.df = None
        self.results_dir = os.path.abspath("analysis_results")

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._setup_directories()

    def _setup_directories(self):
        # sets up where the results are saved
        try:
            os.makedirs(self.results_dir, exist_ok=True)
            print(f"\n[STATUS] the results will be saved to: {self.results_dir}")
        except Exception as e:
            print(f"\n[WARNING] error: could not create the primary results directory: {str(e)}")
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            self.results_dir = os.path.join(desktop, "cosmetics_analysis")
            os.makedirs(self.results_dir, exist_ok=True)
            print(f"[FALLBACK] using desktop directory: {self.results_dir}")

    def load_data(self):
        # ^---this loads and proccesses the cosmetic data
        print("\n[1/5] Loading data...")
        try:
            abs_path = os.path.abspath(self.data_path)
            print(f"looking for data at: {abs_path}")
            
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"error: the data file not found at {abs_path}")
            
            self.df = pd.read_csv(abs_path)
            
            # cleaning the data

            # this converts the date columns to datetime
            date_cols = ['InitialDateReported', 'MostRecentDateReported', 
                        'DiscontinuedDate', 'ChemicalCreatedAt', 
                        'ChemicalUpdatedAt']
            
            for col in date_cols:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            
            # adding a year column
            if 'InitialDateReported' in self.df.columns:
                self.df['ReportYear'] = self.df['InitialDateReported'].dt.year
            
            print(f"yay! Success!! Loaded {len(self.df)} records")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] oh no! Failed to load data: {str(e)}")
            return False

    def basic_analysis(self):
        # ^----basic data exploration
        print("\n[2/5] beep boop running basic analysis......")
        
        # the data structure
        print("\n---- Data Structure ----")
        print(f"Total records: {len(self.df)}")
        print("\nData types:")
        print(self.df.dtypes)
        
        # dealing with missing values
        print("\n---- Missing Values ----")
        print(self.df.isnull().sum())
        
        # dealing with unique counts
        print("\n---- Unique Counts ----")
        cat_cols = ['CompanyName', 'BrandName', 'PrimaryCategory', 'SubCategory', 'ChemicalName']
        for col in cat_cols:
            if col in self.df.columns:
                print(f"{col}: {self.df[col].nunique()} unique values")

    def chemical_analysis(self):
        # ^---this analyzes the chemical patterns
        print("\n[3/5] beep boop analyzing chemical data.....")
        
        # what are the most common chemicals 
        chem_counts = self.df['ChemicalName'].value_counts()
        print("\n---- Top Chemicals ----")
        print(chem_counts.head(20))
        
        # organizing the chemicals by catagory
        print("\n---- Chemicals by Catagory ----")
        chem_by_category = self.df.groupby(['PrimaryCategory', 'ChemicalName']).size()
        print(chem_by_category.head(20))
        
        # the trends over time
        if 'ReportYear' in self.df.columns:
            print("\n---- Chemical Trends over Time ----")
            chem_trends = self.df.groupby(['ReportYear', 'ChemicalName']).size().unstack()
            print(chem_trends.sum(axis=1))  # chem per year
            
            # plotting the top 5 chemicals over time
            top_chems = chem_counts.head(5).index
            plt.figure(figsize=(12, 6))
            for chem in top_chems:
                if chem in chem_trends.columns:
                    plt.plot(chem_trends.index, chem_trends[chem], label=chem)
            plt.title('Top 5 Chemicals Over Time')
            plt.xlabel('Year')
            plt.ylabel('Number of Products')
            plt.legend()
            self._save_plot('chemical_trends.png')
            plt.close()

    def product_analysis(self):
        """Analyze product patterns"""
        print("\n[4/5] Analyzing product data...")
        
        # statistics about the companies
        print("\n---- Company Statistics ----")
        company_stats = self.df.groupby('CompanyName').agg({
            'ProductName': 'nunique',
            'ChemicalName': 'nunique'
        }).sort_values('ProductName', ascending=False)
        print(company_stats.head(10))
        
        # distrobution of the catagories
        print("\n---- Catagory Distrobution ----")
        category_dist = self.df['PrimaryCategory'].value_counts()
        print(category_dist)
        
        # subcategory analysis
        print("\n---- Subcatagory Breakdown ----")
        subcat_dist = self.df.groupby(['PrimaryCategory', 'SubCategory']).size()
        print(subcat_dist.head(20))
        
        # the discontinued products
        if 'DiscontinuedDate' in self.df.columns:
            discontinued = self.df[self.df['DiscontinuedDate'].notna()]
            print(f"\n--- Discontinued Products: {len(discontinued)} ===")
            
            if len(discontinued) > 0:
                # for gathering infromation about why chemicals may have been discontinued based off when it happened
                disc_chem = discontinued['ChemicalName'].value_counts()
                print("\nChemicals in discontinued products:")
                print(disc_chem.head(10))
                
                # plotting why they were discontinued
                plt.figure(figsize=(10, 6))
                disc_chem.head(10).plot(kind='bar')
                plt.title('Top Chemicals in Discontinued Products')
                plt.xticks(rotation=45)
                self._save_plot('discontinued_chemicals.png')
                plt.close()

    def advanced_analysis(self):
        # ^---more advanced analysis
        print("\n[5/5] beep boop running advanced analyses...")
        
        # the combinations of chemicls 
        print("\n---- Chemical Combinations ----")
        product_chems = self.df.groupby('ProductName')['ChemicalName'].unique()
        print(f"\nAverage chemicals per product: {product_chems.apply(len).mean():.1f}")
        
        # the chemicals profiles of each brans 
        print("\n---- Brand Chemical Profiles ----")
        brand_chems = self.df.groupby('BrandName')['ChemicalName'].nunique().sort_values(ascending=False)
        print(brand_chems.head(10))
        
        # the diversity of chemicals for each brand 
        print("\nChemical Diversity by Catagory")
        category_diversity = self.df.groupby('PrimaryCategory')['ChemicalName'].nunique()
        print(category_diversity.sort_values(ascending=False))

    def _save_plot(self, filename):
        # ^---- saves the matplotlib figures
        path = os.path.join(self.results_dir, f"{self.timestamp}_{filename}")
        plt.savefig(path, bbox_inches='tight')
        print(f"Saved plot: {filename}")

    def save_results(self):
        # saves all the results
        print("\nbeep boop saving results...")
        
        try:
            # saving the cleaned data
            data_path = os.path.join(self.results_dir, f"{self.timestamp}_cleaned_data.csv")
            self.df.to_csv(data_path, index=False)
            
            # saving the chemical counts
            chem_path = os.path.join(self.results_dir, f"{self.timestamp}_chemical_counts.csv")
            self.df['ChemicalName'].value_counts().to_csv(chem_path, header=['Count'])
            
            # saving the company statistics
            company_path = os.path.join(self.results_dir, f"{self.timestamp}_company_stats.csv")
            self.df.groupby('CompanyName').agg({
                'ProductName': 'nunique',
                'ChemicalName': 'nunique'
            }).to_csv(company_path)
            
            print(f"Results saved to: {self.results_dir}")
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")

    def run_full_analysis(self):
        # BEEP BOOP RUN COMPLETE ANALYSIS
        if not self.load_data():
            return
            
        self.basic_analysis()
        self.chemical_analysis()
        self.product_analysis()
        self.advanced_analysis()
        self.save_results()

if __name__ == "__main__":
    # the absoultue path
    DATA_FILE = os.path.abspath("data/chemicals-in-cosmetics.csv")
    
    print("---- Cosmetic Data Analysis ----")
    analyzer = CosmeticsAnalyzer(DATA_FILE)
    analyzer.run_full_analysis()
    
    # to keep the terminal open 
    if 'python' in sys.executable.lower():
        input("\nPress Enter to exit...")