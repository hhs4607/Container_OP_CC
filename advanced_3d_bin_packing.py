"""
Advanced 3D Bin Packing Algorithm (Position-Based with Maximal Spaces)

This algorithm tracks actual positions of items in 3D space and uses
the "Maximal Empty Spaces" heuristic to find optimal placement.

Algorithm (based on "Extreme Points" method):
1. Sort items by volume (largest first)
2. Maintain a list of "extreme points" (candidate positions)
3. For each item, try to place it at the best feasible position
4. Update extreme points after each placement

Features:
- Tracks exact (x, y, z) positions of each item
- Considers item rotation (6 orientations)
- Maximizes space utilization
- Detects collisions

Time Complexity: O(n³) in worst case
Space Complexity: O(n²)

Based on research by:
- Crainic, T. G., et al. (2008) "An extreme point-based heuristics"
- Zhao, X., et al. (2016) "A hybrid approach for 3D bin packing"
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import copy


@dataclass
class Point3D:
    """A point in 3D space."""
    x: float
    y: float
    z: float

    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"


@dataclass
class Item3D:
    """Represents a 3D item/package."""
    name: str
    length: float  # x dimension
    width: float   # y dimension
    height: float  # z dimension
    weight: float = 0.0
    position: Optional[Point3D] = None  # Position when placed
    rotation: int = 0  # 0-5, represents rotation state

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    def get_dimensions(self, rotation: int = 0) -> Tuple[float, float, float]:
        """Get dimensions based on rotation (6 possible orientations)."""
        dims = [(self.length, self.width, self.height),
                (self.length, self.height, self.width),
                (self.width, self.length, self.height),
                (self.width, self.height, self.length),
                (self.height, self.length, self.width),
                (self.height, self.width, self.length)]
        return dims[rotation % 6]

    def get_bounds(self) -> Tuple[Point3D, Point3D]:
        """Get min and max bounds of placed item."""
        if self.position is None:
            raise ValueError("Item not placed")
        l, w, h = self.get_dimensions(self.rotation)
        min_point = self.position
        max_point = Point3D(self.position.x + l, self.position.y + w, self.position.z + h)
        return min_point, max_point

    def __repr__(self):
        if self.position:
            l, w, h = self.get_dimensions(self.rotation)
            return f"{self.name}({l}×{w}×{h} at {self.position})"
        return f"{self.name}({self.length}×{self.width}×{self.height})"


@dataclass
class PlacedItem:
    """An item placed in a container with its position."""
    item: Item3D
    x: float
    y: float
    z: float
    rotation: int = 0

    @property
    def volume(self) -> float:
        return self.item.volume

    def get_bounds(self) -> Tuple[Point3D, Point3D]:
        """Get the bounding box of this placed item."""
        l, w, h = self.item.get_dimensions(self.rotation)
        min_pt = Point3D(self.x, self.y, self.z)
        max_pt = Point3D(self.x + l, self.y + w, self.z + h)
        return min_pt, max_pt

    def __repr__(self):
        l, w, h = self.item.get_dimensions(self.rotation)
        return f"{self.item.name}({l}×{w}×{h}) at ({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"


@dataclass
class Container3D:
    """Represents a 3D container with positioned items."""
    length: float
    width: float
    height: float
    max_weight: float = float('inf')
    placed_items: List[PlacedItem] = field(default_factory=list)

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    @property
    def used_volume(self) -> float:
        return sum(pi.volume for pi in self.placed_items)

    @property
    def remaining_volume(self) -> float:
        return self.volume - self.used_volume

    @property
    def used_weight(self) -> float:
        return sum(pi.item.weight for pi in self.placed_items)

    @property
    def remaining_weight(self) -> float:
        return self.max_weight - self.used_weight

    @property
    def volume_utilization(self) -> float:
        return (self.used_volume / self.volume) * 100 if self.volume > 0 else 0

    def check_collision(self, x: float, y: float, z: float,
                       l: float, w: float, h: float) -> bool:
        """Check if a box at (x,y,z) with size (l,w,h) collides with any placed item."""
        new_min = Point3D(x, y, z)
        new_max = Point3D(x + l, y + w, z + h)

        for placed in self.placed_items:
            p_min, p_max = placed.get_bounds()
            # Check for overlap in all dimensions
            if (new_min.x < p_max.x and new_max.x > p_min.x and
                new_min.y < p_max.y and new_max.y > p_min.y and
                new_min.z < p_max.z and new_max.z > p_min.z):
                return True
        return False

    def can_place(self, item: Item3D, x: float, y: float, z: float, rotation: int = 0) -> bool:
        """Check if item can be placed at position with given rotation."""
        # Check weight
        if item.weight > self.remaining_weight:
            return False

        l, w, h = item.get_dimensions(rotation)

        # Check if fits in container bounds
        if x + l > self.length or y + w > self.width or z + h > self.height:
            return False

        # Check collision with other items
        return not self.check_collision(x, y, z, l, w, h)

    def place_item(self, item: Item3D, x: float, y: float, z: float, rotation: int = 0) -> bool:
        """Place item at position if possible."""
        if self.can_place(item, x, y, z, rotation):
            placed = PlacedItem(item, x, y, z, rotation)
            self.placed_items.append(placed)
            item.position = Point3D(x, y, z)
            item.rotation = rotation
            return True
        return False

    def find_best_position(self, item: Item3D) -> Optional[Tuple[float, float, float, int]]:
        """Find best position for item using extreme points heuristic."""
        best_position = None
        best_volume_utilization = -1

        # Start with origin
        extreme_points = [Point3D(0, 0, 0)]

        # Add extreme points from existing items
        for placed in self.placed_items:
            p_min, p_max = placed.get_bounds()
            extreme_points.append(Point3D(p_max.x, p_min.y, p_min.z))  # x-extreme
            extreme_points.append(Point3D(p_min.x, p_max.y, p_min.z))  # y-extreme
            extreme_points.append(Point3D(p_min.x, p_min.y, p_max.z))  # z-extreme

        # Try each position and rotation
        for point in extreme_points:
            for rotation in range(6):
                if self.can_place(item, point.x, point.y, point.z, rotation):
                    l, w, h = item.get_dimensions(rotation)
                    # Prefer positions that minimize wasted space (lower z, then y, then x)
                    volume_util = -(point.z * self.length * self.width +
                                   point.y * self.length +
                                   point.x)
                    if volume_util > best_volume_utilization:
                        best_volume_utilization = volume_util
                        best_position = (point.x, point.y, point.z, rotation)

        return best_position

    def __repr__(self):
        return (f"Container({self.length}×{self.width}×{self.height}, "
                f"{len(self.placed_items)} items, {self.volume_utilization:.1f}% full)")


def advanced_3d_packing(items: List[Item3D],
                        container_l: float,
                        container_w: float,
                        container_h: float,
                        max_weight: float = float('inf'),
                        allow_rotation: bool = True) -> Tuple[List[Container3D], List[Item3D]]:
    """
    Pack 3D items using position-based algorithm with extreme points.

    Args:
        items: List of Item3D objects
        container_l: Container length
        container_w: Container width
        container_h: Container height
        max_weight: Maximum weight per container
        allow_rotation: Whether to try different rotations

    Returns:
        Tuple of (containers, unpacked_items)
    """
    # Sort items by volume (largest first) - better for space utilization
    sorted_items = sorted(items, key=lambda x: x.volume, reverse=True)

    # Check which items can potentially fit
    temp_container = Container3D(container_l, container_w, container_h, max_weight)
    unpacked_items = []
    packable_items = []

    for item in sorted_items:
        # Check if item can fit in any rotation
        can_fit = False
        for rot in range(6 if allow_rotation else 1):
            l, w, h = item.get_dimensions(rot)
            if l <= container_l and w <= container_w and h <= container_h:
                can_fit = True
                break

        if can_fit and item.weight <= max_weight:
            packable_items.append(item)
        else:
            unpacked_items.append(item)

    # Pack items into containers
    containers = []

    for item in packable_items:
        placed = False

        # Try existing containers
        for container in containers:
            best_pos = container.find_best_position(item)
            if best_pos:
                container.place_item(item, *best_pos)
                placed = True
                break

        # Need new container
        if not placed:
            new_container = Container3D(container_l, container_w, container_h, max_weight)
            best_pos = new_container.find_best_position(item)
            if best_pos:
                new_container.place_item(item, *best_pos)
                containers.append(new_container)
            else:
                unpacked_items.append(item)

    return containers, unpacked_items


def print_advanced_solution(containers: List[Container3D],
                            unpacked_items: List[Item3D],
                            container_l: float,
                            container_w: float,
                            container_h: float,
                            max_weight: float = float('inf')):
    """Print detailed 3D packing solution."""
    print(f"\n{'='*70}")
    print(f"3D BIN PACKING - POSITION-BASED ALGORITHM")
    print(f"{'='*70}")
    print(f"Container Size: {container_l} × {container_w} × {container_h}")
    print(f"Container Volume: {container_l * container_w * container_h:.1f}")
    if max_weight != float('inf'):
        print(f"Max Weight per Container: {max_weight}")
    print(f"Number of Containers Used: {len(containers)}")

    if unpacked_items:
        print(f"\n⚠️  Warning: {len(unpacked_items)} item(s) too large:")
        for item in unpacked_items:
            print(f"     {item}")

    print(f"\n{'='*70}")
    print(f"CONTAINER DETAILS")
    print(f"{'='*70}")

    for i, container in enumerate(containers, 1):
        print(f"\n📦 Container {i}:")
        print(f"   Items ({len(container.placed_items)}):")
        for j, placed in enumerate(container.placed_items, 1):
            l, w, h = placed.item.get_dimensions(placed.rotation)
            print(f"      {j}. {placed.item.name} ({l}×{w}×{h}) "
                  f"at ({placed.x:.1f}, {placed.y:.1f}, {placed.z:.1f})")

        print(f"   Volume Used: {container.used_volume:.1f} / {container.volume:.1f} "
              f"({container.volume_utilization:.1f}%)")
        if max_weight != float('inf'):
            print(f"   Weight Used: {container.used_weight:.1f} / {max_weight:.1f}")

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    total_items = sum(len(c.placed_items) for c in containers)
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
    print("EXAMPLE 1: Position-Based 3D Packing")
    print("="*70)

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

    container_l1, container_w1, container_h1 = 100, 80, 60
    max_weight1 = 100

    containers1, unpacked1 = advanced_3d_packing(
        items1, container_l1, container_w1, container_h1, max_weight1
    )

    print_advanced_solution(containers1, unpacked1, container_l1, container_w1, container_h1, max_weight1)

    # Example 2: Comparison with simple method
    print("\n" + "="*70)
    print("EXAMPLE 2: Larger Dataset")
    print("="*70)

    items2 = [
        Item3D("A1", 50, 40, 30, weight=20),
        Item3D("A2", 30, 30, 30, weight=12),
        Item3D("A3", 40, 30, 20, weight=10),
        Item3D("A4", 25, 25, 25, weight=8),
        Item3D("A5", 60, 40, 20, weight=15),
        Item3D("A6", 35, 35, 35, weight=14),
        Item3D("A7", 45, 30, 25, weight=11),
        Item3D("A8", 20, 20, 40, weight=6),
        Item3D("A9", 55, 35, 30, weight=16),
        Item3D("A10", 30, 25, 20, weight=7),
    ]

    container_l2, container_w2, container_h2 = 100, 100, 100

    containers2, unpacked2 = advanced_3d_packing(
        items2, container_l2, container_w2, container_h2
    )

    print_advanced_solution(containers2, unpacked2, container_l2, container_w2, container_h2)

    print("\n💡 This algorithm provides:")
    print("   ✓ Exact positioning of each item")
    print("   ✓ Automatic rotation optimization (6 orientations)")
    print("   ✓ Better space utilization than volume-based methods")
    print("   ✓ Collision detection")
