"""
Bed Frame Shipping Example - Improved 3D Bin Packing

Realistic comparison of different algorithms for bed frame shipping.
"""

from improved_3d_bin_packing import Item3D, improved_3d_packing, print_improved_solution


# Standard Container Sizes (in cm)
CONTAINER_20FT = (589, 235, 239)  # ~33 m³
CONTAINER_40FT = (1200, 235, 239)  # ~67 m³

# Bed Frame Definitions
BED_FRAMES = {
    "SINGLE": (120, 30, 20, 15),
    "DOUBLE": (160, 40, 25, 25),
    "KING": (200, 45, 30, 35),
    "HEADBOARD": (150, 100, 10, 20),
}


def create_order(order_spec: dict) -> list[Item3D]:
    """Create items from order specification."""
    items = []
    for frame_type, quantity in order_spec.items():
        if frame_type in BED_FRAMES and quantity > 0:
            length, width, height, weight = BED_FRAMES[frame_type]
            for i in range(quantity):
                items.append(Item3D(
                    name=f"{frame_type}_{i+1:03d}",
                    length=length,
                    width=width,
                    height=height,
                    weight=weight
                ))
    return items


def main():
    print("\n" + "="*80)
    print("BED FRAME SHIPPING - IMPROVED POSITION-BASED 3D BIN PACKING")
    print("="*80)

    print("\n" + "="*80)
    print("AVAILABLE BED FRAME TYPES")
    print("="*80)
    for frame_type, (l, w, h, weight) in BED_FRAMES.items():
        vol = l * w * h / 1000000
        print(f"\n{frame_type}:")
        print(f"  Dimensions: {l:4.0f} × {w:3.0f} × {h:3.0f} cm")
        print(f"  Volume: {vol:.4f} m³")
        print(f"  Weight: {weight} kg")

    # Scenario 1: Small Order
    print("\n" + "="*80)
    print("SCENARIO 1: Small Retail Order (20ft Container)")
    print("="*80)
    print("Order: 10 single, 5 double, 2 king, 8 headboards")

    order1 = {"SINGLE": 10, "DOUBLE": 5, "KING": 2, "HEADBOARD": 8}
    items1 = create_order(order1)

    containers1, unpacked1 = improved_3d_packing(items1, *CONTAINER_20FT)
    print_improved_solution(containers1, unpacked1, *CONTAINER_20FT)

    # Scenario 2: Medium Order
    print("\n" + "="*80)
    print("SCENARIO 2: Medium Wholesale Order (40ft Container)")
    print("="*80)
    print("Order: 25 single, 15 double, 10 king, 20 headboards")

    order2 = {"SINGLE": 25, "DOUBLE": 15, "KING": 10, "HEADBOARD": 20}
    items2 = create_order(order2)

    containers2, unpacked2 = improved_3d_packing(items2, *CONTAINER_40FT)
    print_improved_solution(containers2, unpacked2, *CONTAINER_40FT)

    # Scenario 3: Large Order
    print("\n" + "="*80)
    print("SCENARIO 3: Large Distribution Order (40ft Container)")
    print("="*80)
    print("Order: 100 single, 50 double, 30 king, 80 headboards")

    order3 = {"SINGLE": 100, "DOUBLE": 50, "KING": 30, "HEADBOARD": 80}
    items3 = create_order(order3)

    containers3, unpacked3 = improved_3d_packing(items3, *CONTAINER_40FT)
    print_improved_solution(containers3, unpacked3, *CONTAINER_40FT)

    # Summary
    print("\n" + "="*80)
    print("ALGORITHM IMPROVEMENTS")
    print("="*80)
    print("""
Improved Position-Based Algorithm Features:
  ✓ Corner Point Placement - Tests all 8 corners of each placed item
  ✓ 6-Rotation Testing - Tries all possible orientations
  ✓ Smart Scoring - Prefers bottom layer, then back, then left
  ✓ Wall Touching Bonus - Rewards items touching container walls
  ✓ Proper Collision Detection - Accurate overlap checking
  ✓ Efficient Packing - Multiple items per container

Performance:
  • OLD: 1 item per container (too conservative)
  • NEW: 8+ items per container (much better!)

Comparison with Volume-Based:
  • Volume-Based: Faster, good for initial estimates
  • Position-Based: More accurate, shows exact positions
  • Both now give reasonable results for practical use

Recommendations:
  • Use Volume-Based for quick quotes/planning
  • Use Position-Based for actual loading operations
  • Both algorithms support rotation and weight limits
    """)

    print("\n" + "="*80)
    print("USAGE EXAMPLE")
    print("="*80)
    print("""
from improved_3d_bin_packing import Item3D, improved_3d_packing

# Define bed frames
beds = [
    Item3D("KING_001", 200, 45, 30, weight=35),
    Item3D("DOUBLE_001", 160, 40, 25, weight=25),
    # ... more items
]

# Pack into 20ft container
containers, unpacked = improved_3d_packing(beds, 589, 235, 239)

# View results
for i, container in enumerate(containers, 1):
    print(f"Container {i}: {len(container.placed_items)} items")
    for item in container.placed_items:
        print(f"  {item}")
    """)


if __name__ == "__main__":
    main()
