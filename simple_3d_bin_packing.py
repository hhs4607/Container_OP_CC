"""
Simple 3D Bin Packing Algorithm (Volume-Based Approach)

This is a simplified 3D bin packing that uses volume as the primary constraint.
It's faster but less optimal than position-based algorithms.

Algorithm:
1. Sort items by volume (largest first)
2. Place each item in the first container that has enough volume remaining
3. Checks if individual dimensions fit (L, W, H must all be ≤ container dimensions)

Limitations:
- Does not optimize actual positioning
- May overestimate space usage
- Does not consider complex item rotations

Time Complexity: O(n log n) + O(n²)
Space Complexity: O(n)
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Item3D:
    """Represents a 3D item/package."""
    name: str
    length: float  # x dimension
    width: float   # y dimension
    height: float  # z dimension
    weight: float = 0.0  # optional weight constraint

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    def can_rotate_to_fit(self, container_l, container_w, container_h) -> bool:
        """Check if item can fit in container with any rotation."""
        dimensions = [self.length, self.width, self.height]
        # Try all 6 possible rotations
        for i in range(3):
            for j in range(3):
                if j == i:
                    continue
                for k in range(3):
                    if k == i or k == j:
                        continue
                    if (dimensions[i] <= container_l and
                        dimensions[j] <= container_w and
                        dimensions[k] <= container_h):
                        return True
        return False

    def __repr__(self):
        return f"{self.name}({self.length}×{self.width}×{self.height}, vol:{self.volume:.1f})"


@dataclass
class Container3D:
    """Represents a 3D container/bin."""
    length: float
    width: float
    height: float
    max_weight: float = float('inf')  # optional weight limit
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
    def remaining_volume(self) -> float:
        return self.volume - self.used_volume

    @property
    def used_weight(self) -> float:
        return sum(item.weight for item in self.items)

    @property
    def remaining_weight(self) -> float:
        return self.max_weight - self.used_weight

    @property
    def volume_utilization(self) -> float:
        return (self.used_volume / self.volume) * 100 if self.volume > 0 else 0

    def can_fit(self, item: Item3D) -> bool:
        """Check if item can fit in this container."""
        # Check volume
        if item.volume > self.remaining_volume:
            return False

        # Check weight
        if item.weight > self.remaining_weight:
            return False

        # Check if item can fit with rotation
        return item.can_rotate_to_fit(self.length, self.width, self.height)

    def add_item(self, item: Item3D) -> bool:
        """Add item to container if it fits."""
        if self.can_fit(item):
            self.items.append(item)
            return True
        return False

    def __repr__(self):
        return (f"Container({self.length}×{self.width}×{self.height}, "
                f"{len(self.items)} items, {self.volume_utilization:.1f}% full)")


def simple_3d_first_fit_decreasing(items: List[Item3D],
                                    container_l: float,
                                    container_w: float,
                                    container_h: float,
                                    max_weight: float = float('inf')) -> Tuple[List[Container3D], List[Item3D]]:
    """
    Pack 3D items into containers using First Fit Decreasing (volume-based).

    Args:
        items: List of Item3D objects
        container_l: Container length
        container_w: Container width
        container_h: Container height
        max_weight: Maximum weight per container (optional)

    Returns:
        Tuple of (containers, unpacked_items)
    """
    # Sort items by volume (largest first)
    sorted_items = sorted(items, key=lambda x: x.volume, reverse=True)

    # Separate items that are too large
    unpacked_items = []
    packable_items = []

    temp_container = Container3D(container_l, container_w, container_h, max_weight)
    for item in sorted_items:
        if temp_container.can_fit(item):
            packable_items.append(item)
        else:
            unpacked_items.append(item)

    # Initialize containers
    containers = []

    # Pack each item
    for item in packable_items:
        placed = False

        # Try to place in existing containers
        for container in containers:
            if container.add_item(item):
                placed = True
                break

        # Create new container if needed
        if not placed:
            new_container = Container3D(container_l, container_w, container_h, max_weight)
            new_container.add_item(item)
            containers.append(new_container)

    return containers, unpacked_items


def print_solution_3d(containers: List[Container3D],
                      unpacked_items: List[Item3D],
                      container_l: float,
                      container_w: float,
                      container_h: float,
                      max_weight: float = float('inf')):
    """Print the 3D packing solution."""
    print(f"\n{'='*70}")
    print(f"3D BIN PACKING - VOLUME-BASED FIRST FIT DECREASING")
    print(f"{'='*70}")
    print(f"Container Size: {container_l} × {container_w} × {container_h}")
    print(f"Container Volume: {container_l * container_w * container_h:.1f}")
    if max_weight != float('inf'):
        print(f"Max Weight per Container: {max_weight}")
    print(f"Number of Containers Used: {len(containers)}")

    if unpacked_items:
        print(f"\n⚠️  Warning: {len(unpacked_items)} item(s) too large for containers:")
        for item in unpacked_items:
            print(f"     {item}")

    print(f"\n{'='*70}")
    print(f"CONTAINER DETAILS")
    print(f"{'='*70}")

    for i, container in enumerate(containers, 1):
        print(f"\n📦 Container {i}:")
        print(f"   Items ({len(container.items)}):")
        for j, item in enumerate(container.items, 1):
            print(f"      {j}. {item}")
        print(f"   Volume Used: {container.used_volume:.1f} / {container.volume:.1f} "
              f"({container.volume_utilization:.1f}%)")
        if max_weight != float('inf'):
            print(f"   Weight Used: {container.used_weight:.1f} / {max_weight:.1f}")

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    total_items = sum(len(c.items) for c in containers)
    total_volume_used = sum(c.used_volume for c in containers)
    total_volume_capacity = len(containers) * container_l * container_w * container_h
    overall_efficiency = (total_volume_used / total_volume_capacity) * 100

    print(f"  Total Items Packed: {total_items}")
    print(f"  Total Volume Used: {total_volume_used:.1f} / {total_volume_capacity:.1f}")
    print(f"  Overall Volume Efficiency: {overall_efficiency:.1f}%")
    print(f"{'='*70}\n")


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("EXAMPLE 1: Standard 3D Box Packing")
    print("="*70)

    # Define items (packages)
    items1 = [
        Item3D("Box1", 30, 20, 10, weight=5),
        Item3D("Box2", 40, 30, 20, weight=10),
        Item3D("Box3", 25, 25, 15, weight=7),
        Item3D("Box4", 50, 40, 30, weight=15),
        Item3D("Box5", 20, 15, 10, weight=3),
        Item3D("Box6", 35, 25, 20, weight=8),
        Item3D("Box7", 45, 35, 25, weight=12),
        Item3D("Box8", 15, 15, 15, weight=4),
    ]

    # Define container size (e.g., standard shipping container)
    container_l1, container_w1, container_h1 = 100, 80, 60
    max_weight1 = 100

    containers1, unpacked1 = simple_3d_first_fit_decreasing(
        items1, container_l1, container_w1, container_h1, max_weight1
    )

    print_solution_3d(containers1, unpacked1, container_l1, container_w1, container_h1, max_weight1)

    # Example 2: Different sizes
    print("\n" + "="*70)
    print("EXAMPLE 2: Mixed Package Sizes")
    print("="*70)

    items2 = [
        Item3D("Package_A", 60, 40, 30, weight=20),
        Item3D("Package_B", 30, 20, 20, weight=5),
        Item3D("Package_C", 50, 50, 40, weight=25),
        Item3D("Package_D", 25, 25, 25, weight=8),
        Item3D("Package_E", 70, 30, 35, weight=18),
        Item3D("Package_F", 40, 40, 30, weight=15),
        Item3D("Package_G", 20, 20, 20, weight=4),
    ]

    container_l2, container_w2, container_h2 = 100, 100, 100

    containers2, unpacked2 = simple_3d_first_fit_decreasing(
        items2, container_l2, container_w2, container_h2
    )

    print_solution_3d(containers2, unpacked2, container_l2, container_w2, container_h2)

    print("\n💡 Usage:")
    print("   from simple_3d_bin_packing import Item3D, simple_3d_first_fit_decreasing")
    print("   items = [Item3D('name', length, width, height, weight)]")
    print("   containers, unpacked = simple_3d_first_fit_decreasing(items, L, W, H, max_weight)")
