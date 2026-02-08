"""
First Fit Decreasing (FFD) Algorithm for Bin Packing

This algorithm packs items into bins by:
1. Sorting items in decreasing order (largest first)
2. Placing each item in the first bin that has enough space
3. Creating a new bin if no existing bin can hold the item

Time Complexity: O(n log n) for sorting + O(n²) for packing
Space Complexity: O(n)
"""

def first_fit_decreasing(items, bin_capacity):
    """
    Pack items into bins using First Fit Decreasing algorithm.

    Args:
        items: List of item sizes (positive numbers)
        bin_capacity: Maximum capacity of each bin

    Returns:
        Tuple of (bins, num_bins, unpacked_items)
        - bins: List of lists showing items in each bin
        - num_bins: Total number of bins used
        - unpacked_items: Items that couldn't fit (larger than bin capacity)
    """
    # Sort items in decreasing order
    sorted_items = sorted(items, reverse=True)

    # Separate items that are too large for any bin
    unpacked_items = [item for item in sorted_items if item > bin_capacity]
    packable_items = [item for item in sorted_items if item <= bin_capacity]

    # Initialize bins
    bins = []

    # Pack each item
    for item in packable_items:
        placed = False

        # Try to place in existing bins (first fit)
        for bin in bins:
            if sum(bin) + item <= bin_capacity:
                bin.append(item)
                placed = True
                break

        # If couldn't place in existing bins, create new bin
        if not placed:
            bins.append([item])

    return bins, len(bins), unpacked_items


def print_solution(bins, num_bins, unpacked_items, bin_capacity):
    """Print the solution in a readable format."""
    print(f"\n{'='*60}")
    print(f"FIRST FIT DECREASING ALGORITHM")
    print(f"{'='*60}")
    print(f"Bin Capacity: {bin_capacity}")
    print(f"Number of Bins Used: {num_bins}")

    if unpacked_items:
        print(f"\nWarning: {len(unpacked_items)} item(s) too large for bins:")
        for item in unpacked_items:
            print(f"  - {item}")

    print(f"\nBin Contents:")
    print(f"{'-'*60}")

    for i, bin in enumerate(bins, 1):
        bin_usage = sum(bin)
        usage_percent = (bin_usage / bin_capacity) * 100
        print(f"Bin {i}: {bin} (Total: {bin_usage}/{bin_capacity}, {usage_percent:.1f}%)")

    print(f"{'-'*60}")
    total_items = sum(len(bin) for bin in bins)
    total_capacity_used = sum(sum(bin) for bin in bins)
    total_capacity_available = num_bins * bin_capacity
    overall_efficiency = (total_capacity_used / total_capacity_available) * 100

    print(f"\nSummary:")
    print(f"  Total Items Packed: {total_items}")
    print(f"  Total Capacity Used: {total_capacity_used}/{total_capacity_available}")
    print(f"  Overall Efficiency: {overall_efficiency:.1f}%")
    print(f"{'='*60}\n")


# Example usage and test cases
if __name__ == "__main__":
    # Example 1: Standard test case
    print("\n" + "="*60)
    print("EXAMPLE 1: Standard Container Packing")
    print("="*60)

    items1 = [4, 8, 1, 4, 2, 1, 8, 5, 3, 2]
    capacity1 = 10

    print(f"\nItems to pack: {items1}")
    print(f"Bin capacity: {capacity1}")

    bins1, num_bins1, unpacked1 = first_fit_decreasing(items1, capacity1)
    print_solution(bins1, num_bins1, unpacked1, capacity1)

    # Example 2: Larger items
    print("\n" + "="*60)
    print("EXAMPLE 2: Random Package Sizes")
    print("="*60)

    items2 = [23, 45, 12, 34, 56, 18, 29, 41, 7, 15]
    capacity2 = 60

    print(f"\nItems to pack: {items2}")
    print(f"Bin capacity: {capacity2}")

    bins2, num_bins2, unpacked2 = first_fit_decreasing(items2, capacity2)
    print_solution(bins2, num_bins2, unpacked2, capacity2)

    # Example 3: User input example
    print("\n" + "="*60)
    print("EXAMPLE 3: Custom Input")
    print("="*60)
    print("\nYou can modify this code to accept custom input:")
    print("  bins, num_bins, unpacked = first_fit_decreasing(your_items, your_capacity)")
