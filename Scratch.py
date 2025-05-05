import requests
from bs4 import BeautifulSoup
import csv
import concurrent.futures
import time

# Base URL pattern
base_url = "https://results.beup.ac.in/ResultsBTech6thSem2024_B2021Pub.aspx?Sem=VI&RegNo={}"

# Branch codes mapping
branch_codes = {
    "101": "Civil Engineering (CE)",
    "102": "Mechanical Engineering (ME)",
    "103": "Electrical Engineering (EE)",
    "104": "Electronics & Communication Engineering (ECE)",
    "105": "Computer Science Engineering (CSE)",
    "106": "Information Technology (IT)",
    "107": "Leather Technology (LT)",
    "110": "Electrical & Electronics Engineering (EEE)",
    "111": "Instrumentation Engineering (IE)"
}

# College codes range (102 to 165)
college_codes = [str(i).zfill(3) for i in range(102, 166)]  # 102 to 165 inclusive

# Batch year (21 for 2021)
batch_year = "21"

# Student number range
range_start = 1
range_end = 130
max_workers = 10  # Number of concurrent threads
failed_attempts_threshold = 5  # Skip branch after this many consecutive failures

# Output CSV file
output_file = "all_branches_results.csv"

# Initialize CSV file
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Registration Number", "Name", "Father's Name", "Mother's Name", 
                     "College Name", "College Code", "Branch Name", "Branch Code", 
                     "SGPA", "Cur. CGPA"])

def generate_prefixes():
    prefixes = []
    for branch_code in branch_codes.keys():
        for college_code in college_codes:
            prefix = f"{batch_year}{branch_code}{college_code}"
            prefixes.append(prefix)
    return prefixes

def process_registration(reg_no, session):
    result_url = base_url.format(reg_no)
    try:
        response = session.get(result_url, timeout=10)
        
        # Skip if page doesn't exist or returns error
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Check if this is a valid result page (not an error page)
        name_tag = soup.find("span", {"id": "ContentPlaceHolder1_DataList1_StudentNameLabel_0"})
        if not name_tag:
            return None
            
        name = name_tag.text.strip()
        
        # Extract Father's Name
        father_tag = soup.find("span", {"id": "ContentPlaceHolder1_DataList1_FatherNameLabel_0"})
        father_name = father_tag.text.strip() if father_tag else "Not Found"
        
        # Extract Mother's Name
        mother_tag = soup.find("span", {"id": "ContentPlaceHolder1_DataList1_MotherNameLabel_0"})
        mother_name = mother_tag.text.strip() if mother_tag else "Not Found"
        
        # Extract College Name and Code
        college_name = "Not Found"
        college_code = reg_no[5:8]  # Extract college code from registration number
        college_tag = soup.find("span", {"id": "ContentPlaceHolder1_DataList1_CollegeNameLabel_0"})
        if college_tag:
            college_name = college_tag.text.strip()
        
        # Extract Branch Name and Code
        branch_name = "Not Found"
        branch_code = reg_no[2:5]  # Extract branch code from registration number
        branch_tag = soup.find("span", {"id": "ContentPlaceHolder1_DataList1_CourseLabel_0"})
        if branch_tag:
            branch_name = branch_tag.text.strip()
        
        # Extract SGPA
        sgpa_tag = soup.find("span", {"id": "ContentPlaceHolder1_DataList5_GROSSTHEORYTOTALLabel_0"})
        sgpa = sgpa_tag.text.strip() if sgpa_tag else "Not Found"
        
        # Extract Cur. CGPA from the last <td> in the table
        cur_cgpa = "Not Found"
        table = soup.find("table", {"id": "ContentPlaceHolder1_GridView3"})
        if table:
            rows = table.find_all("tr")
            if len(rows) > 1:
                last_row = rows[1]  # The second row contains CGPA values
                cells = last_row.find_all("td")
                if cells:
                    cur_cgpa = cells[-1].text.strip()  # Last column is "Cur. CGPA"
        
        return [
            reg_no, name, father_name, mother_name, 
            college_name, college_code, 
            branch_name, branch_code,
            sgpa, cur_cgpa
        ]
        
    except Exception as e:
        print(f"Error processing {reg_no}: {str(e)}")
        return None

def process_branch(prefix, session):
    results = []
    consecutive_failures = 0
    
    for i in range(range_start, range_end + 1):
        reg_no = f"{prefix}{str(i).zfill(3)}"
        result = process_registration(reg_no, session)
        
        if result:
            results.append(result)
            consecutive_failures = 0
            print(f"Processed: {reg_no} | Name: {result[1]} | College: {result[4]} ({result[5]}) | Branch: {result[6]} ({result[7]})")
        else:
            consecutive_failures += 1
            if consecutive_failures >= failed_attempts_threshold:
                print(f"Stopping prefix {prefix} after {failed_attempts_threshold} consecutive failures")
                break
    
    return results

def main():
    # Generate all possible prefixes
    prefixes = generate_prefixes()
    print(f"Generated {len(prefixes)} prefixes to check")
    
    # Create a session to reuse connections
    with requests.Session() as session:
        # Set headers to mimic a browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Process prefixes in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # Submit all prefixes for processing
            for prefix in prefixes:
                futures.append(executor.submit(process_branch, prefix, session))
                time.sleep(0.1)  # Small delay between starting threads
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    branch_results = future.result()
                    if branch_results:
                        # Append results to CSV
                        with open(output_file, "a", newline="", encoding="utf-8") as file:
                            writer = csv.writer(file)
                            writer.writerows(branch_results)
                except Exception as e:
                    print(f"Error in branch processing: {str(e)}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\nCompleted in {end_time - start_time:.2f} seconds")
    print(f"Results saved in {output_file}")