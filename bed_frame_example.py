"""
3D Bin Packing - Bed Frame Shipping Example (Position-Based)

Realistic example for shipping bed frame combinations in standard containers.

This example demonstrates the Position-Based algorithm which provides:
- Exact (x, y, z) positioning of each package
- Collision detection
- Automatic rotation optimization
- Better accuracy for physical shipping

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

# Import position-based algorithm
try:
    from advanced_3d_bin_packing import Item3D, Container3D, advanced_3d_packing
except ImportError:
    print("Error: Make sure advanced_3d_bin_packing.py is in the same directory")
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


def create_items_from_order(order_spec: dict) -> List[Item3D]:
    """
    Create Item3D objects from order specification.

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


def print_packing_results(order_name: str, items: List[Item3D],
                          container_l: float, container_w: float, container_h: float,
                          max_weight: float = float('inf')):
    """Print detailed packing results."""

    print(f"\n{'='*80}")
    print(f"ORDER: {order_name}")
    print(f"{'='*80}")

    # Count items by type
    item_counts = {}
    for item in items:
        prefix = item.name.split('_')[0]
        item_counts[prefix] = item_counts.get(prefix, 0) + 1

    print(f"Order Summary:")
    for frame_type, count in sorted(item_counts.items()):
        if frame_type in BED_FRAMES:
            print(f"  - {BED_FRAMES[frame_type]['name']}: {count} units")

    print(f"\nContainer Size: {container_l} × {container_w} × {container_h} cm")
    print(f"Container Volume: {container_l * container_w * container_h / 1000000:.2f} m³")

    # Pack items
    containers, unpacked = advanced_3d_packing(
        items, container_l, container_w, container_h, max_weight, allow_rotation=True
    )

    # Print results
    total_volume = container_l * container_w * container_h
    total_capacity = len(containers) * total_volume
    total_used = sum(c.used_volume for c in containers)

    print(f"\n{'─'*80}")
    print(f"PACKING RESULTS")
    print(f"{'─'*80}")
    print(f"Containers Needed: {len(containers)}")

    if unpacked:
        print(f"\n⚠️  Warning: {len(unpacked)} item(s) could not be packed:")
        for item in unpacked:
            print(f"     - {item}")

    print(f"\nContainer Breakdown:")
    for i, container in enumerate(containers, 1):
        print(f"\n  📦 Container {i}:")
        print(f"     Items: {len(container.placed_items)}")
        print(f"     Volume Used: {container.used_volume / 1000000:.2f} m³ / {total_volume / 1000000:.2f} m³ "
              f"({container.volume_utilization:.1f}%)")

        # Show item positions (first 5 items per container)
        if container.placed_items:
            print(f"     Item Positions:")
            for j, placed in enumerate(container.placed_items[:5], 1):
                l, w, h = placed.item.get_dimensions(placed.rotation)
                print(f"       {j}. {placed.item.name} ({l:.0f}×{w:.0f}×{h:.0f} cm) "
                      f"at ({placed.x:.0f}, {placed.y:.0f}, {placed.z:.0f})")

            if len(container.placed_items) > 5:
                print(f"       ... and {len(container.placed_items) - 5} more items")

    # Summary statistics
    print(f"\n{'─'*80}")
    print(f"SUMMARY STATISTICS")
    print(f"{'─'*80}")
    print(f"Total Items: {len(items)}")
    print(f"Successfully Packed: {len(items) - len(unpacked)}")
    print(f"Containers Used: {len(containers)}")
    print(f"Overall Volume Efficiency: {(total_used / total_capacity * 100):.1f}%")
    avg_items_per_container = len(items) / len(containers)
    print(f"Average Items per Container: {avg_items_per_container:.1f}")

    return containers, unpacked


def main():
    """Run example scenarios for bed frame shipping."""

    print("\n" + "="*80)
    print("BED FRAME SHIPPING - POSITION-BASED 3D BIN PACKING")
    print("="*80)

    print("\n" + "="*80)
    print("AVAILABLE BED FRAME TYPES")
    print("="*80)
    for frame_type, info in BED_FRAMES.items():
        l, w, h = info["dimensions"]
        vol = l * w * h / 1000000  # Convert to m³
        print(f"\n{frame_type}:")
        print(f"  Name: {info['name']}")
        print(f"  Dimensions: {l:4.0f} × {w:3.0f} × {h:3.0f} cm")
        print(f"  Volume: {vol:.4f} m³")
        print(f"  Weight: {info['weight']} kg")
        print(f"  Description: {info['description']}")

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
    items1 = create_items_from_order(order1)
    containers1, unpacked1 = print_packing_results(
        "Small Retail Order", items1, *CONTAINER_20FT
    )

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
    items2 = create_items_from_order(order2)
    containers2, unpacked2 = print_packing_results(
        "Medium Wholesale Order", items2, *CONTAINER_40FT
    )

    # Example 3: Large Order
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
    items3 = create_items_from_order(order3)
    containers3, unpacked3 = print_packing_results(
        "Large Distribution Order", items3, *CONTAINER_40FT
    )

    # Recommendations
    print("\n" + "="*80)
    print("SHIPPING RECOMMENDATIONS")
    print("="*80)
    print("""
Based on the Position-Based 3D Bin Packing Algorithm:

1. Capacity Guidelines:
   • 20ft container (589×235×239 cm): ~30-50 bed frame kits
   • 40ft container (1200×235×239 cm): ~60-100 bed frame kits

2. Efficiency Tips:
   • Mix different bed sizes for better space utilization
   • Consider palletizing for easier handling
   • Leave 5-10% buffer for irregular items
   • Position-based algorithm shows exact placement coordinates

3. Algorithm Benefits:
   ✓ Exact (x, y, z) positioning for warehouse operations
   ✓ Automatic rotation optimization (6 orientations)
   ✓ Collision detection prevents overlapping
   ✓ Realistic packing estimates

4. Usage:
   Use this algorithm for:
   - Final packing plans
   - Warehouse loading instructions
   - Shipping quotes
   - Route optimization
    """)

    print("\n" + "="*80)
    print("CUSTOM ORDER CALCULATOR")
    print("="*80)
    print("\nTo calculate your own order, use:")
    print("""
from bed_frame_example import create_items_from_order, print_packing_results
from advanced_3d_bin_packing import advanced_3d_packing

# Define your order
my_order = {
    "SINGLE": 20,    # 20 single bed frames
    "DOUBLE": 15,    # 15 double bed frames
    "KING": 10,      # 10 king bed frames
    "HEADBOARD": 25  # 25 headboards
}

# Create items
items = create_items_from_order(my_order)

# Pack into 20ft container (589×235×239 cm)
containers, unpacked = advanced_3d_packing(items, 589, 235, 239)

print(f"Containers needed: {len(containers)}")
for i, container in enumerate(containers, 1):
    print(f"Container {i}: {len(container.placed_items)} items "
          f"({container.volume_utilization:.1f}%)")
    """)


if __name__ == "__main__":
    main()
