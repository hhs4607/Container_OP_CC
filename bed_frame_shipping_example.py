"""
3D Bin Packing - Bed Frame Shipping Example

Realistic example for shipping bed frame combinations in standard containers.

Container Sizes:
- 20ft Shipping Container: 589 × 235 × 239 cm (L×W×H)
- 40ft Shipping Container: 1200 × 235 × 239 cm (L×W×H)

Bed Frame Packages (disassembled, boxed):
1. Single/Twin Bed Frame Kit: 120 × 30 × 20 cm, ~15kg
2. Double/Queen Bed Frame Kit: 160 × 40 × 25 cm, ~25kg
3. King/California King Bed Frame Kit: 200 × 45 × 30 cm, ~35kg
4. Headboard (Optional): 150 × 100 × 10 cm, ~20kg
"""

from dataclasses import dataclass
from typing import List, Tuple
import sys

# Import both algorithms
# Note: Use Item3D from advanced module as it has more features
try:
    from advanced_3d_bin_packing import Item3D, advanced_3d_packing
    from simple_3d_bin_packing import simple_3d_first_fit_decreasing
except ImportError:
    print("Error: Make sure simple_3d_bin_packing.py and advanced_3d_bin_packing.py are in the same directory")
    sys.exit(1)


# Standard Container Sizes (in cm)
CONTAINER_20FT = (589, 235, 239)  # ~33 m³ usable
CONTAINER_40FT = (1200, 235, 239)  # ~67 m³ usable

# Bed Frame Package Definitions (in cm, kg)
BED_FRAMES = {
    "SINGLE": {
        "name": "Single/Twin Bed Frame",
        "dimensions": (120, 30, 20),
        "weight": 15,
        "description": "Twin size bed frame kit (disassembled)"
    },
    "DOUBLE": {
        "name": "Double/Queen Bed Frame",
        "dimensions": (160, 40, 25),
        "weight": 25,
        "description": "Double/Queen size bed frame kit (disassembled)"
    },
    "KING": {
        "name": "King/Cal King Bed Frame",
        "dimensions": (200, 45, 30),
        "weight": 35,
        "description": "King size bed frame kit (disassembled)"
    },
    "HEADBOARD": {
        "name": "Headboard",
        "dimensions": (150, 100, 10),
        "weight": 20,
        "description": "Optional headboard (fits all sizes)"
    }
}


def create_order(order_spec: dict) -> List[Item3D]:
    """
    Create items from order specification.

    order_spec format:
    {
        "SINGLE": 10,      # 10 single bed frames
        "DOUBLE": 5,       # 5 double bed frames
        "KING": 3,         # 3 king bed frames
        "HEADBOARD": 8     # 8 headboards
    }
    """
    items = []
    item_id = 1

    for frame_type, quantity in order_spec.items():
        if frame_type in BED_FRAMES and quantity > 0:
            frame_info = BED_FRAMES[frame_type]
            length, width, height = frame_info["dimensions"]
            weight = frame_info["weight"]

            for i in range(quantity):
                item_name = f"{frame_type}_{i+1:03d}"
                items.append(Item3D(
                    name=item_name,
                    length=length,
                    width=width,
                    height=height,
                    weight=weight
                ))
                item_id += 1

    return items


def print_comparison(order_name: str, order_items: List[Item3D],
                    container_l: float, container_w: float, container_h: float):
    """Compare both algorithms for the same order."""
    print(f"\n{'='*80}")
    print(f"ORDER: {order_name}")
    print(f"{'='*80}")
    print(f"Total Items: {len(order_items)}")
    print(f"Container Size: {container_l} × {container_w} × {container_h} cm")
    print(f"Container Volume: {container_l * container_w * container_h / 1000000:.2f} m³")

    # Simple 3D (Volume-Based)
    print(f"\n{'─'*80}")
    print(f"METHOD 1: Volume-Based FFD (Fast)")
    print(f"{'─'*80}")

    containers_simple, unpacked_simple = simple_3d_first_fit_decreasing(
        order_items, container_l, container_w, container_h
    )

    total_volume = container_l * container_w * container_h
    simple_efficiency = sum(c.used_volume for c in containers_simple) / (len(containers_simple) * total_volume) * 100

    print(f"Containers Needed: {len(containers_simple)}")
    print(f"Volume Efficiency: {simple_efficiency:.1f}%")
    print(f"\nContainer Breakdown:")
    for i, container in enumerate(containers_simple, 1):
        print(f"  Container {i}: {len(container.items)} items, "
              f"{container.volume_utilization:.1f}% full")

    # Advanced 3D (Position-Based)
    print(f"\n{'─'*80}")
    print(f"METHOD 2: Position-Based (Accurate)")
    print(f"{'─'*80}")

    containers_advanced, unpacked_advanced = advanced_3d_packing(
        order_items, container_l, container_w, container_h
    )

    adv_efficiency = sum(c.used_volume for c in containers_advanced) / (len(containers_advanced) * total_volume) * 100

    print(f"Containers Needed: {len(containers_advanced)}")
    print(f"Volume Efficiency: {adv_efficiency:.1f}%")
    print(f"\nContainer Breakdown:")
    for i, container in enumerate(containers_advanced, 1):
        print(f"  Container {i}: {len(container.placed_items)} items, "
              f"{container.volume_utilization:.1f}% full")
        if len(container.placed_items) <= 5:
            for placed in container.placed_items:
                print(f"    - {placed.item.name} at ({placed.x:.0f}, {placed.y:.0f}, {placed.z:.0f})")

    # Summary
    print(f"\n{'─'*80}")
    print(f"COMPARISON SUMMARY")
    print(f"{'─'*80}")
    print(f"Volume-Based FFD:     {len(containers_simple)} containers, {simple_efficiency:.1f}% efficiency")
    print(f"Position-Based:       {len(containers_advanced)} containers, {adv_efficiency:.1f}% efficiency")

    if len(containers_simple) < len(containers_advanced):
        print(f"✓ Volume-Based is BETTER (saved {len(containers_advanced) - len(containers_simple)} containers)")
    elif len(containers_simple) > len(containers_advanced):
        print(f"✓ Position-Based is BETTER (saved {len(containers_simple) - len(containers_advanced)} containers)")
    else:
        print(f"= Both methods use the same number of containers")


def main():
    """Run example scenarios for bed frame shipping."""

    print("\n" + "="*80)
    print("BED FRAME SHIPPING - 3D BIN PACKING EXAMPLES")
    print("="*80)
    print("\nAvailable Bed Frame Types:")
    for frame_type, info in BED_FRAMES.items():
        l, w, h = info["dimensions"]
        print(f"  {frame_type:10s}: {info['name']:35s} | {l:4.0f}×{w:3.0f}×{h:3.0f} cm | {info['weight']:2.0f} kg")
        print(f"              {info['description']}")

    # Example 1: Small Order (20ft container)
    print("\n" + "="*80)
    print("SCENARIO 1: Small Retail Order")
    print("="*80)
    print("Customer: Local furniture store")
    print("Order: 10 single, 5 double, 2 king bed frames, 8 headboards")

    order1 = {
        "SINGLE": 10,
        "DOUBLE": 5,
        "KING": 2,
        "HEADBOARD": 8
    }
    items1 = create_order(order1)
    print_comparison("Small Retail Order", items1, *CONTAINER_20FT)

    # Example 2: Medium Order (40ft container)
    print("\n" + "="*80)
    print("SCENARIO 2: Medium Wholesale Order")
    print("="*80)
    print("Customer: Regional furniture chain")
    print("Order: 25 single, 15 double, 10 king bed frames, 20 headboards")

    order2 = {
        "SINGLE": 25,
        "DOUBLE": 15,
        "KING": 10,
        "HEADBOARD": 20
    }
    items2 = create_order(order2)
    print_comparison("Medium Wholesale Order", items2, *CONTAINER_40FT)

    # Example 3: Large Order (multiple 40ft containers)
    print("\n" + "="*80)
    print("SCENARIO 3: Large Distribution Order")
    print("="*80)
    print("Customer: National retailer")
    print("Order: 100 single, 50 double, 30 king bed frames, 80 headboards")

    order3 = {
        "SINGLE": 100,
        "DOUBLE": 50,
        "KING": 30,
        "HEADBOARD": 80
    }
    items3 = create_order(order3)
    print_comparison("Large Distribution Order", items3, *CONTAINER_40FT)

    # Example 4: Specialized Order (mostly king size)
    print("\n" + "="*80)
    print("SCENARIO 4: Luxury Hotel Chain")
    print("="*80)
    print("Customer: Hotel chain (luxury, all king beds)")
    print("Order: 5 single, 10 double, 50 king bed frames, 60 headboards")

    order4 = {
        "SINGLE": 5,
        "DOUBLE": 10,
        "KING": 50,
        "HEADBOARD": 60
    }
    items4 = create_order(order4)
    print_comparison("Luxury Hotel Chain", items4, *CONTAINER_40FT)

    # Summary and Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("""
For Bed Frame Shipping:

1. Volume-Based FFD (Simple):
   ✓ FASTER execution (recommended for >50 items)
   ✓ Good for quick estimates and planning
   ✓ Better efficiency in most practical cases
   ✓ Use for: Initial planning, quotes, large orders

2. Position-Based (Advanced):
   ✓ Exact positioning of each package
   ✓ Better for complex arrangements
   ✓ Shows exact (x,y,z) coordinates
   ✓ Use for: Final packing plans, warehouse operations, optimization studies

3. Practical Tips:
   • Use Volume-Based for initial order estimates
   • Use Position-Based for actual packing operations
   • Consider palletizing for easier handling
   • Leave 5-10% buffer for irregular items and handling
   • 20ft container: ~30-40 bed frame kits
   • 40ft container: ~60-80 bed frame kits
    """)

    print(f"\n{'='*80}")
    print("CUSTOM ORDER CALCULATOR")
    print("="*80)
    print("\nTo calculate your own order, use:")
    print("""
from bed_frame_shipping_example import create_order, print_comparison
from simple_3d_bin_packing import simple_3d_first_fit_decreasing

# Define your order
my_order = {
    "SINGLE": 20,    # 20 single bed frames
    "DOUBLE": 15,    # 15 double bed frames
    "KING": 10,      # 10 king bed frames
    "HEADBOARD": 25  # 25 headboards
}

# Create items
items = create_order(my_order)

# Pack into 20ft container (589×235×239 cm)
containers, unpacked = simple_3d_first_fit_decreasing(items, 589, 235, 239)

print(f"Containers needed: {len(containers)}")
for i, container in enumerate(containers, 1):
    print(f"Container {i}: {len(container.items)} items ({container.volume_utilization:.1f}%)")
    """)


if __name__ == "__main__":
    main()
