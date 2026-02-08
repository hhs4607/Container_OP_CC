"""
Bed Frame Shipping Example with 3D Visualization

This example demonstrates:
1. Container utilization (volume and weight)
2. Position of each item (x, y, z coordinates)
3. 3D visualization from multiple views (ISO, Top, Front, Side)

Results are saved to the 'results' folder.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from improved_3d_bin_packing import Item3D, improved_3d_packing, Container3D, PlacedItem

# Container sizes (in cm)
CONTAINER_20FT = (589, 235, 239)
CONTAINER_40FT = (1200, 235, 239)

# Bed frame definitions
BED_FRAMES = {
    "SINGLE": {"dims": (120, 30, 20), "weight": 15, "color": "#3498db"},
    "DOUBLE": {"dims": (160, 40, 25), "weight": 25, "color": "#e74c3c"},
    "KING": {"dims": (200, 45, 30), "weight": 35, "color": "#2ecc71"},
    "HEADBOARD": {"dims": (150, 100, 10), "weight": 20, "color": "#f39c12"},
}


def create_order(order_spec: dict) -> list[Item3D]:
    """Create items from order specification."""
    items = []
    for frame_type, quantity in order_spec.items():
        if frame_type in BED_FRAMES and quantity > 0:
            length, width, height = BED_FRAMES[frame_type]["dims"]
            weight = BED_FRAMES[frame_type]["weight"]
            for i in range(quantity):
                items.append(Item3D(
                    name=f"{frame_type}_{i+1:03d}",
                    length=length,
                    width=width,
                    height=height,
                    weight=weight
                ))
    return items


def save_results_to_file(containers: list[Container3D],
                        unpacked: list[Item3D],
                        container_dims: tuple,
                        output_file: str):
    """Save detailed packing results to a text file."""

    container_l, container_w, container_h = container_dims
    container_volume = container_l * container_w * container_h

    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("BED FRAME SHIPPING - PACKING RESULTS\n")
        f.write("="*80 + "\n\n")

        f.write(f"Container Dimensions: {container_l} × {container_w} × {container_h} cm\n")
        f.write(f"Container Volume: {container_volume / 1000000:.2f} m³\n")
        f.write(f"Number of Containers Used: {len(containers)}\n\n")

        # Summary statistics
        total_items = sum(len(c.placed_items) for c in containers)
        total_volume_used = sum(c.used_volume for c in containers)
        total_weight = sum(sum(p.item.weight for p in c.placed_items) for c in containers)
        total_capacity = len(containers) * container_volume

        f.write("="*80 + "\n")
        f.write("SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Total Items Packed: {total_items}\n")
        f.write(f"Total Volume Used: {total_volume_used / 1000000:.2f} / {total_capacity / 1000000:.2f} m³ "
                f"({(total_volume_used / total_capacity * 100):.1f}%)\n")
        f.write(f"Total Weight: {total_weight:.1f} kg\n")
        f.write(f"Average Items per Container: {total_items / len(containers):.1f}\n\n")

        if unpacked:
            f.write(f"Unpacked Items: {len(unpacked)}\n")
            for item in unpacked:
                f.write(f"  - {item}\n")
            f.write("\n")

        # Detailed container information
        f.write("="*80 + "\n")
        f.write("DETAILED CONTAINER INFORMATION\n")
        f.write("="*80 + "\n\n")

        for i, container in enumerate(containers, 1):
            container_weight = sum(p.item.weight for p in container.placed_items)

            f.write(f"CONTAINER {i}\n")
            f.write("-"*80 + "\n")
            f.write(f"Items: {len(container.placed_items)}\n")
            f.write(f"Volume Used: {container.used_volume / 1000000:.2f} / {container.volume / 1000000:.2f} m³ "
                    f"({container.volume_utilization:.1f}%)\n")
            f.write(f"Weight Used: {container_weight:.1f} kg\n\n")

            f.write("ITEM POSITIONS:\n")
            f.write("-"*80 + "\n")
            f.write(f"{'No.':<5} {'Item Name':<20} {'Dimensions (cm)':<20} {'Position (x,y,z)':<20} {'Weight':<10}\n")
            f.write("-"*80 + "\n")

            for j, placed in enumerate(container.placed_items, 1):
                dims_str = f"{placed.length:.0f}×{placed.width:.0f}×{placed.height:.0f}"
                pos_str = f"({placed.x:.0f},{placed.y:.0f},{placed.z:.0f})"
                f.write(f"{j:<5} {placed.item.name:<20} {dims_str:<20} {pos_str:<20} {placed.item.weight:<10.1f}\n")

            f.write("\n" + "="*80 + "\n\n")

    print(f"✓ Results saved to: {output_file}")


def create_3d_visualization(containers: list[Container3D],
                            container_dims: tuple,
                            output_folder: str):
    """Create 3D visualization plots from multiple views."""

    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.patches as mpatches
    except ImportError:
        print("⚠️  Matplotlib not installed. Skipping visualization.")
        print("   Install with: pip install matplotlib")
        return

    container_l, container_w, container_h = container_dims

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each container
    for container_idx, container in enumerate(containers, 1):
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle(f'Container {container_idx} - {len(container.placed_items)} Items '
                    f'({container.volume_utilization:.1f}% Full, '
                    f'{sum(p.item.weight for p in container.placed_items):.0f} kg)',
                    fontsize=16, fontweight='bold')

        # Create 4 subplots
        views = [
            (1, "Isometric View (3D)", 20, 45),
            (2, "Top View", 90, -90),
            (3, "Front View", 0, -90),
            (4, "Side View", 0, 0),
        ]

        for subplot_idx, view_name, elev, azim in views:
            ax = fig.add_subplot(2, 2, subplot_idx, projection='3d')
            plot_container_simple(ax, container, container_l, container_w, container_h, elev, azim, view_name)

        # Add legend
        legend_elements = [
            mpatches.Patch(color=BED_FRAMES["SINGLE"]["color"], label='Single Bed Frame'),
            mpatches.Patch(color=BED_FRAMES["DOUBLE"]["color"], label='Double Bed Frame'),
            mpatches.Patch(color=BED_FRAMES["KING"]["color"], label='King Bed Frame'),
            mpatches.Patch(color=BED_FRAMES["HEADBOARD"]["color"], label='Headboard'),
        ]
        fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=10)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        output_file = os.path.join(output_folder, f'container_{container_idx}_3d_views.png')
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ 3D visualization saved to: {output_file}")


def plot_container_simple(ax, container: Container3D,
                         container_l: float, container_w: float, container_h: float,
                         elev: int, azim: int, title: str):
    """Plot a single 3D view of the container using simple approach."""

    # Draw container wireframe using lines
    # Bottom face
    ax.plot([0, container_l, container_l, 0, 0], [0, 0, container_w, container_w, 0], [0, 0, 0, 0, 0], 'k-', linewidth=2, alpha=0.5)
    # Top face
    ax.plot([0, container_l, container_l, 0, 0], [0, 0, container_w, container_w, 0], [container_h, container_h, container_h, container_h, container_h], 'k-', linewidth=2, alpha=0.5)
    # Vertical edges
    ax.plot([0, 0], [0, 0], [0, container_h], 'k-', linewidth=2, alpha=0.5)
    ax.plot([container_l, container_l], [0, 0], [0, container_h], 'k-', linewidth=2, alpha=0.5)
    ax.plot([container_l, container_l], [container_w, container_w], [0, container_h], 'k-', linewidth=2, alpha=0.5)
    ax.plot([0, 0], [container_w, container_w], [0, container_h], 'k-', linewidth=2, alpha=0.5)

    # Draw items using bar3d
    from mpl_toolkits.mplot3d import Axes3D
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        # Draw as a 3D box
        draw_box_edges(ax, placed.x, placed.y, placed.z,
                      placed.length, placed.width, placed.height, color)

    # Set labels and title
    ax.set_xlabel('Length (cm)')
    ax.set_ylabel('Width (cm)')
    ax.set_zlabel('Height (cm)')
    ax.set_title(title)

    # Set aspect ratio
    ax.set_box_aspect([container_l, container_w, container_h])

    # Set limits
    ax.set_xlim(0, container_l)
    ax.set_ylim(0, container_w)
    ax.set_zlim(0, container_h)

    # Set view angle
    ax.view_init(elev=elev, azim=azim)

    # Invert y-axis
    ax.invert_yaxis()


def draw_box_edges(ax, x: float, y: float, z: float,
                  l: float, w: float, h: float,
                  color: str, alpha: float = 0.7):
    """Draw a 3D box with proper faces and edges."""

    # Import Poly3DCollection for proper 3D polygon rendering
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    # Define vertices
    vertices = [
        [x, y, z],
        [x + l, y, z],
        [x + l, y + w, z],
        [x, y + w, z],
        [x, y, z + h],
        [x + l, y, z + h],
        [x + l, y + w, z + h],
        [x, y + w, z + h]
    ]

    # Define faces (6 faces of the box)
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # Back
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # Left
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # Right
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # Top
    ]

    # Draw filled faces with transparency
    face_poly = Poly3DCollection(faces, alpha=alpha*0.4, facecolors=color,
                                 edgecolors=color, linewidths=1.5)
    ax.add_collection3d(face_poly)


def get_item_color(item_name: str) -> str:
    """Get color for item based on type."""
    if item_name.startswith("SINGLE"):
        return BED_FRAMES["SINGLE"]["color"]
    elif item_name.startswith("DOUBLE"):
        return BED_FRAMES["DOUBLE"]["color"]
    elif item_name.startswith("KING"):
        return BED_FRAMES["KING"]["color"]
    elif item_name.startswith("HEADBOARD"):
        return BED_FRAMES["HEADBOARD"]["color"]
    return "#95a5a6"  # Default gray


def main():
    """Main function to run examples and save results."""

    print("\n" + "="*80)
    print("BED FRAME SHIPPING - 3D VISUALIZATION EXAMPLE")
    print("="*80 + "\n")

    # Create results folder
    results_folder = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_folder, exist_ok=True)

    # Example scenarios
    scenarios = [
        {
            "name": "Small Retail Order",
            "description": "10 single, 5 double, 2 king, 8 headboards",
            "container": CONTAINER_20FT,
            "order": {"SINGLE": 10, "DOUBLE": 5, "KING": 2, "HEADBOARD": 8}
        },
        {
            "name": "Medium Wholesale Order",
            "description": "25 single, 15 double, 10 king, 20 headboards",
            "container": CONTAINER_40FT,
            "order": {"SINGLE": 25, "DOUBLE": 15, "KING": 10, "HEADBOARD": 20}
        },
        {
            "name": "Large Distribution Order",
            "description": "50 single, 30 double, 20 king, 40 headboards",
            "container": CONTAINER_40FT,
            "order": {"SINGLE": 50, "DOUBLE": 30, "KING": 20, "HEADBOARD": 40}
        }
    ]

    # Process each scenario
    for scenario_idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"SCENARIO {scenario_idx}: {scenario['name']}")
        print(f"{'='*80}")
        print(f"Description: {scenario['description']}")

        # Create items
        items = create_order(scenario['order'])
        print(f"Total Items: {len(items)}")

        # Pack items
        containers, unpacked = improved_3d_packing(items, *scenario['container'])
        print(f"Containers Needed: {len(containers)}")

        # Save text results
        result_file = os.path.join(results_folder,
                                   f"scenario_{scenario_idx}_{scenario['name'].replace(' ', '_').lower()}.txt")
        save_results_to_file(containers, unpacked, scenario['container'], result_file)

        # Create 3D visualizations
        viz_folder = os.path.join(results_folder, "visualizations")
        create_3d_visualization(containers, scenario['container'], viz_folder)

        # Print summary
        total_items = sum(len(c.placed_items) for c in containers)
        total_volume = sum(c.used_volume for c in containers)
        total_capacity = len(containers) * scenario['container'][0] * scenario['container'][1] * scenario['container'][2]
        total_weight = sum(sum(p.item.weight for p in c.placed_items) for c in containers)

        print(f"\nSummary:")
        print(f"  Items Packed: {total_items}")
        print(f"  Volume Used: {total_volume / 1000000:.2f} / {total_capacity / 1000000:.2f} m³ "
              f"({(total_volume / total_capacity * 100):.1f}%)")
        print(f"  Total Weight: {total_weight:.1f} kg")

    print("\n" + "="*80)
    print("ALL RESULTS SAVED!")
    print("="*80)
    print(f"\nResults folder: {results_folder}")
    print("Contents:")
    print("  - Text files with detailed packing information")
    print("  - 3D visualization plots (4 views per container)")
    print("\nVisualization views:")
    print("  1. Isometric View (3D perspective)")
    print("  2. Top View (looking down)")
    print("  3. Front View (looking from front)")
    print("  4. Side View (looking from side)")


if __name__ == "__main__":
    main()
