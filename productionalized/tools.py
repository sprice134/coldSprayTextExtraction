import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import mean_absolute_error
from difflib import SequenceMatcher
import pdfplumber



def calculate_similarity(exp1, exp2):
    similarity = 0

    # Numeric field similarity (absolute difference)
    for field in ['yield_strength_value', "ultimate_tensile_strength_value", 
                  'ductility_value', 'hardness_value', 'modulus_value']:
        val1 = exp1.get(field, "NA")
        val2 = exp2.get(field, "NA")
        
        # Convert to numeric if possible, otherwise treat "NA" as 0
        try:
            val1 = float(val1) if val1 != "NA" else 0.0
            val2 = float(val2) if val2 != "NA" else 0.0
        except ValueError:
            val1 = val2 = 0.0  # Fallback for unexpected non-numeric strings
        
        # The more the difference, the more we penalize (subtract from similarity)
        similarity -= abs(val1 - val2)

    # Text field similarity (SequenceMatcher)
    notes1 = exp1.get("notes", "")
    notes2 = exp2.get("notes", "")
    similarity += SequenceMatcher(None, notes1, notes2).ratio()

    return similarity


def rmse(gt_values, ext_values):
    return np.sqrt(np.mean((np.array(gt_values) - np.array(ext_values)) ** 2))

def calculate_performance(ground_truth, extracted, penalty=1.0):
    num_ground_truth = len(ground_truth)
    num_extracted = len(extracted)
    similarity_matrix = np.zeros((num_ground_truth, num_extracted))

    # Calculate similarity matrix
    for i, gt in enumerate(ground_truth):
        for j, ext in enumerate(extracted):
            similarity_matrix[i, j] = calculate_similarity(gt, ext)

    # Optimal matching using Hungarian Algorithm
    row_ind, col_ind = linear_sum_assignment(-similarity_matrix)  # Maximize similarity

    # Create matched pairs and identify unmatched
    matched_pairs = []
    matched_gt = set(row_ind)
    matched_ext = set(col_ind)
    
    for i, j in zip(row_ind, col_ind):
        matched_pairs.append((ground_truth[i], extracted[j]))

    unmatched_gt = set(range(num_ground_truth)) - matched_gt
    unmatched_ext = set(range(num_extracted)) - matched_ext

    # Calculate individual performance metrics (normalized RMSE)
    field_rmse = {}
    normalized_losses = []

    for field in ['yield_strength_value', "ultimate_tensile_strength_value", 'ductility_value', 'hardness_value', 'modulus_value']:
        gt_values = []
        ext_values = []

        # Process matched pairs only
        for gt, ext in matched_pairs:
            gt_val = gt.get(field, "NA")
            ext_val = ext.get(field, "NA")
            # Convert "NA" or invalid types to 0
            gt_val = float(gt_val) if isinstance(gt_val, (int, float)) else 0
            ext_val = float(ext_val) if isinstance(ext_val, (int, float)) else 0
            gt_values.append(gt_val)
            ext_values.append(ext_val)

        # Compute RMSE and normalize
        if gt_values and ext_values:
            error = rmse(gt_values, ext_values)
            max_gt_value = max(gt_values) if gt_values else 1  # Avoid division by 0
            normalized_loss = error / max_gt_value if max_gt_value != 0 else 0
            field_rmse[field] = normalized_loss
            normalized_losses.append(normalized_loss)

    # Calculate overall loss
    avg_normalized_loss = np.mean(normalized_losses) if normalized_losses else 0
    if num_ground_truth > 0:
        percent_error = abs(num_extracted - num_ground_truth) / num_ground_truth
    else:
        # Apply penalty proportional to the number of extracted items
        percent_error = num_extracted
    overall_loss = avg_normalized_loss + (percent_error * penalty)

    # Display Results
    results = {
        "Field RMSE": field_rmse,  # Normalized individual metrics
        "Overall Loss": overall_loss,  # Penalized overall performance
        "Similarity Matrix": similarity_matrix,
        "Unmatched Ground Truth": unmatched_gt,
        "Unmatched Extracted": unmatched_ext
    }
    return results

def calculate_performance_V2(ground_truth, extracted, penalty=1.0):
    """
    Calculate performance metrics between ground_truth and extracted.
    This function excludes any final "metadata" object containing 
    'Extracted_paper_author', 'Extracted_publication_year', 
    and 'graph_verification_required' from matching & evaluation.
    """
    # Separate out the "metadata" or "final" objects from extracted
    excluded_info = []
    extracted_filtered = []

    for ext_obj in extracted:
        # Check if this object is the "metadata" object
        if all(k in ext_obj for k in [
            "Extracted_paper_author", 
            "Extracted_publication_year", 
            "graph_verification_required"
        ]):
            excluded_info.append(ext_obj)
        else:
            extracted_filtered.append(ext_obj)

    # Count how many final/metadata objects were flagged for additional checking
    flagged_for_additional_checking = sum(
        1 
        for item in excluded_info 
        if item.get("graph_verification_required") == "HIGH"
    )
    # Count how many final/metadata objects had "LOW" verification
    ignored_count = sum(
        1 
        for item in excluded_info 
        if item.get("graph_verification_required") == "LOW"
    )

    # Now proceed with the standard performance calculation on the filtered set
    num_ground_truth = len(ground_truth)
    num_extracted = len(extracted_filtered)
    similarity_matrix = np.zeros((num_ground_truth, num_extracted))

    # Calculate similarity matrix
    for i, gt in enumerate(ground_truth):
        for j, ext in enumerate(extracted_filtered):
            similarity_matrix[i, j] = calculate_similarity(gt, ext)

    # Optimal matching using Hungarian Algorithm (maximize similarity => minimize negative)
    row_ind, col_ind = linear_sum_assignment(-similarity_matrix)

    # Build matched pairs
    matched_pairs = []
    matched_gt = set(row_ind)
    matched_ext = set(col_ind)
    
    for i, j in zip(row_ind, col_ind):
        matched_pairs.append((ground_truth[i], extracted_filtered[j]))

    unmatched_gt = set(range(num_ground_truth)) - matched_gt
    unmatched_ext = set(range(num_extracted)) - matched_ext

    # Calculate individual performance metrics (normalized RMSE)
    field_rmse = {}
    normalized_losses = []

    for field in ['yield_strength_value', "ultimate_tensile_strength_value",
                  'ductility_value', 'hardness_value', 'modulus_value']:
        gt_values = []
        ext_values = []

        # Process matched pairs only
        for gt, ext in matched_pairs:
            gt_val = gt.get(field, "NA")
            ext_val = ext.get(field, "NA")
            # Convert "NA" or invalid to 0
            try:
                gt_val = float(gt_val)
            except:
                gt_val = 0.0
            try:
                ext_val = float(ext_val)
            except:
                ext_val = 0.0

            gt_values.append(gt_val)
            ext_values.append(ext_val)

        # Compute RMSE and normalize
        if gt_values and ext_values:
            error = rmse(gt_values, ext_values)
            max_gt_value = max(gt_values) if gt_values else 1  # Avoid division by 0
            normalized_loss = error / max_gt_value if max_gt_value != 0 else 0
            field_rmse[field] = normalized_loss
            normalized_losses.append(normalized_loss)

    # Calculate overall loss
    avg_normalized_loss = np.mean(normalized_losses) if normalized_losses else 0
    if num_ground_truth > 0:
        # Penalize difference in count
        percent_error = abs(num_extracted - num_ground_truth) / num_ground_truth
    else:
        # If we have no ground truth, any extraction is penalized
        percent_error = num_extracted

    overall_loss = avg_normalized_loss + (percent_error * penalty)

    # Summarize results
    results = {
        "Field RMSE": field_rmse,
        "Overall Loss": overall_loss,
        "Similarity Matrix": similarity_matrix,
        "Unmatched Ground Truth": unmatched_gt,
        "Unmatched Extracted": unmatched_ext,
        "Flagged for Additional Checking (HIGH)": flagged_for_additional_checking,
        "Ignored Count (LOW)": ignored_count
    }

    return results




def pdf_to_text(pdf_path):
    """
    Extract text from a PDF and return it as a single string.
    """
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)