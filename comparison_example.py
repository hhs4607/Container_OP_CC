"""
Simple Bed Frame Packing Example - Volume-Based (Practical)

This uses the VOLUME-BASED approach which is faster and gives better results
for most practical shipping scenarios.
"""

from dataclasses import dataclass
from typing import List


# Define a simple Item3D class for this example
@dataclass
class Item3D:
    """Represents a 3D item/package."""
    name: str
    length: float
    width: float
    height: float
    weight: float = 0.0

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass
class Container3D:
    """Represents a 3D container/bin."""
    length: float
    width: float
    height: float
    max_weight: float = float('inf')
    items: List[Item3D] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    @property
    def used_volume(self) -> float:
        return sum(item.volume for item in self.items)

    @property
    def volume_utilization(self) -> float:
        return (self.used_volume / self.volume) * 100 if self.volume > 0 else 0


def volume_based_ffd(items: List[Item3D], container_l: float, container_w: float, container_h: float) -> List[Container3D]:
    """Volume-based First Fit Decreasing algorithm."""
    # Sort items by volume (largest first)
    sorted_items = sorted(items, key=lambda x: x.volume, reverse=True)

    # Initialize containers
    containers = []

    # Pack each item
    for item in sorted_items:
        placed = False

        # Try to place in existing containers
        for container in containers:
            if (container.used_volume + item.volume <= container.volume and
                item.length <= container.length and
                item.width <= container.width and
                item.height <= container.height):
                container.items.append(item)
                placed = True
                break

        # Create new container if needed
        if not placed:
            new_container = Container3D(container_l, container_w, container_h)
            new_container.items.append(item)
            containers.append(new_container)

    return containers


# Standard Container Sizes (in cm)
CONTAINER_20FT = (589, 235, 239)
CONTAINER_40FT = (1200, 235, 239)

# Bed Frame Definitions
BED_FRAMES = {
    "SINGLE": (120, 30, 20, 15),    # L, W, H, weight (cm, kg)
    "DOUBLE": (160, 40, 25, 25),
    "KING": (200, 45, 30, 35),
    "HEADBOARD": (150, 100, 10, 20),
}


def create_order(order_spec: dict) -> List[Item3D]:
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
    print("="*80)
    print("BED FRAME SHIPPING - VOLUME-BASED PACKING (PRACTICAL)")
    print("="*80)

    # Scenario 1: Small Order
    print("\n" + "="*80)
    print("SCENARIO 1: Small Retail Order")
    print("="*80)
    print("Order: 10 single, 5 double, 2 king bed frames, 8 headboards")
    print("Container: 20ft (589×235×239 cm)")

    order1 = {"SINGLE": 10, "DOUBLE": 5, "KING": 2, "HEADBOARD": 8}
    items1 = create_order(order1)

    containers1 = volume_based_ffd(items1, *CONTAINER_20FT)

    print(f"\nResults:")
    print(f"  Total Items: {len(items1)}")
    print(f"  Containers Needed: {len(containers1)}")

    for i, container in enumerate(containers1, 1):
        print(f"\n  Container {i}:")
        print(f"    Items: {len(container.items)}")
        print(f"    Volume: {container.used_volume/1000000:.2f} / {container.volume/1000000:.2f} m³ "
              f"({container.volume_utilization:.1f}%)")

    # Scenario 2: Medium Order
    print("\n" + "="*80)
    print("SCENARIO 2: Medium Wholesale Order")
    print("="*80)
    print("Order: 25 single, 15 double, 10 king bed frames, 20 headboards")
    print("Container: 40ft (1200×235×239 cm)")

    order2 = {"SINGLE": 25, "DOUBLE": 15, "KING": 10, "HEADBOARD": 20}
    items2 = create_order(order2)

    containers2 = volume_based_ffd(items2, *CONTAINER_40FT)

    print(f"\nResults:")
    print(f"  Total Items: {len(items2)}")
    print(f"  Containers Needed: {len(containers2)}")

    for i, container in enumerate(containers2, 1):
        print(f"\n  Container {i}:")
        print(f"    Items: {len(container.items)}")
        print(f"    Volume: {container.used_volume/1000000:.2f} / {container.volume/1000000:.2f} m³ "
              f"({container.volume_utilization:.1f}%)")

    # Scenario 3: Large Order
    print("\n" + "="*80)
    print("SCENARIO 3: Large Distribution Order")
    print("="*80)
    print("Order: 100 single, 50 double, 30 king bed frames, 80 headboards")
    print("Container: 40ft (1200×235×239 cm)")

    order3 = {"SINGLE": 100, "DOUBLE": 50, "KING": 30, "HEADBOARD": 80}
    items3 = create_order(order3)

    containers3 = volume_based_ffd(items3, *CONTAINER_40FT)

    print(f"\nResults:")
    print(f"  Total Items: {len(items3)}")
    print(f"  Containers Needed: {len(containers3)}")

    for i, container in enumerate(containers3[:5], 1):  # Show first 5
        print(f"\n  Container {i}:")
        print(f"    Items: {len(container.items)}")
        print(f"    Volume: {container.used_volume/1000000:.2f} / {container.volume/1000000:.2f} m³ "
              f"({container.volume_utilization:.1f}%)")

    if len(containers3) > 5:
        print(f"\n  ... and {len(containers3) - 5} more containers")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"""
Volume-Based FFD Performance:
  ✓ Fast execution
  ✓ Good space utilization
  ✓ Practical for real-world shipping

Container Capacity Guidelines:
  • 20ft container: ~30-50 bed frame kits
  • 40ft container: ~60-100 bed frame kits

For your orders:
  • Scenario 1 (25 items): {len(containers1)} containers (20ft)
  • Scenario 2 (70 items): {len(containers2)} containers (40ft)
  • Scenario 3 (260 items): {len(containers3)} containers (40ft)
    """)


if __name__ == "__main__":
    main()
