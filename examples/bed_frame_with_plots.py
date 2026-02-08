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

# Import matplotlib here for 2D patches
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.patches as mpatches
except ImportError:
    matplotlib = None

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
    """Create two separate figure files: 3D Isometric View and Orthographic Projection."""

    if matplotlib is None:
        print("⚠️  Matplotlib not installed. Skipping visualization.")
        print("   Install with: pip install matplotlib")
        return

    container_l, container_w, container_h = container_dims

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each container
    for container_idx, container in enumerate(containers, 1):
        # ========================================
        # FIGURE A: 3D Isometric View (Standalone)
        # ========================================
        create_figure_3d_isometric(container, container_idx, container_l, container_w, container_h, output_folder)

        # ========================================
        # FIGURE B: Orthographic Projection (2D Connected Views)
        # ========================================
        create_figure_orthographic(container, container_idx, container_l, container_w, container_h, output_folder)


def create_figure_3d_isometric(container: Container3D, container_idx: int,
                                container_l: float, container_w: float, container_h: float,
                                output_folder: str):
    """Create standalone 3D isometric view figure."""

    # Calculate figure size based on container's longest dimension
    max_dim = max(container_l, container_w, container_h)
    figsize = max_dim / 50  # Scale: 50cm per inch

    fig = plt.figure(figsize=(figsize, figsize * 0.75))
    fig.suptitle(f'Container {container_idx} - 3D Isometric View\n'
                f'{len(container.placed_items)} Items ({container.volume_utilization:.1f}% Full, '
                f'{sum(p.item.weight for p in container.placed_items):.0f} kg)',
                fontsize=12, fontweight='bold')

    ax = fig.add_subplot(111, projection='3d')
    plot_container_3d(ax, container, container_l, container_w, container_h,
                     elev=20, azim=45, title="")

    # Add legend
    legend_elements = [
        mpatches.Patch(color=BED_FRAMES["SINGLE"]["color"], label='Single Bed Frame'),
        mpatches.Patch(color=BED_FRAMES["DOUBLE"]["color"], label='Double Bed Frame'),
        mpatches.Patch(color=BED_FRAMES["KING"]["color"], label='King Bed Frame'),
        mpatches.Patch(color=BED_FRAMES["HEADBOARD"]["color"], label='Headboard'),
    ]
    fig.legend(handles=legend_elements, loc='outside lower center',
              ncol=4, fontsize=9, frameon=True)

    output_file = os.path.join(output_folder, f'container_{container_idx}_isometric_3d.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"✓ 3D Isometric view saved to: {output_file}")


def create_figure_orthographic(container: Container3D, container_idx: int,
                               container_l: float, container_w: float, container_h: float,
                               output_folder: str):
    """Create orthographic projection with connected 2D views (technical drawing style)."""

    # Calculate figure size to maintain aspect ratio
    # Layout is 2x2: Top View + Legend on top row, Front + Side on bottom row
    # Width driven by Length (Top/Front) + Width (Side)
    # Height driven by Width (Top) + Height (Front/Side)

    width_ratio = (container_l + container_w) / max(container_l, container_w, container_h)
    height_ratio = (container_w + container_h) / max(container_l, container_w, container_h)

    base_size = 12
    fig_width = base_size * width_ratio
    fig_height = base_size * height_ratio

    fig = plt.figure(figsize=(fig_width, fig_height), layout='constrained')
    fig.suptitle(f'Container {container_idx} - Orthographic Projection\n'
                f'{len(container.placed_items)} Items ({container.volume_utilization:.1f}% Full)',
                fontsize=11, fontweight='bold')

    # Create 2x2 grid with minimal spacing for "connected" look
    # Layout:
    #   Top-Left (ax1): Top View (Length vs Width)
    #   Top-Right (ax2): Legend (empty plot for legend)
    #   Bottom-Left (ax3): Front View (Length vs Height) - shares X with Top View
    #   Bottom-Right (ax4): Side View (Width vs Height) - shares Y with Front View

    gs = fig.add_gridspec(2, 2, hspace=0.05, wspace=0.05,
                          height_ratios=[container_w, container_h],
                          width_ratios=[container_l, container_w])

    # Top-Left: Top View (Length vs Width)
    ax1 = fig.add_subplot(gs[0, 0])
    plot_container_2d_top_connected(ax1, container, container_l, container_w, container_h,
                                    title="Top View (X-Y Plane)")

    # Top-Right: Legend area
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')
    legend_elements = [
        mpatches.Patch(color=BED_FRAMES["SINGLE"]["color"], label='Single Bed Frame'),
        mpatches.Patch(color=BED_FRAMES["DOUBLE"]["color"], label='Double Bed Frame'),
        mpatches.Patch(color=BED_FRAMES["KING"]["color"], label='King Bed Frame'),
        mpatches.Patch(color=BED_FRAMES["HEADBOARD"]["color"], label='Headboard'),
    ]
    ax2.legend(handles=legend_elements, loc='center', fontsize=9,
               frameon=True, shadow=True)

    # Bottom-Left: Front View (Length vs Height) - shares X-axis with Top View
    ax3 = fig.add_subplot(gs[1, 0], sharex=ax1)
    plot_container_2d_front_connected(ax3, container, container_l, container_w, container_h,
                                      title="Front View (X-Z Plane)")

    # Bottom-Right: Side View (Width vs Height) - shares Y-axis with Front View
    ax4 = fig.add_subplot(gs[1, 1])
    plot_container_2d_side_connected(ax4, container, container_l, container_w, container_h,
                                     title="Side View (Y-Z Plane)")

    output_file = os.path.join(output_folder, f'container_{container_idx}_orthographic_2d.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"✓ Orthographic 2D view saved to: {output_file}")


def plot_container_3d(ax, container: Container3D,
                      container_l: float, container_w: float, container_h: float,
                      elev: int, azim: int, title: str):
    """Plot 3D isometric view with proper box aspect ratio."""

    # Draw container wireframe
    draw_container_wireframe_3d(ax, container_l, container_w, container_h)

    # Draw items
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        draw_box_3d(ax, placed.x, placed.y, placed.z,
                   placed.length, placed.width, placed.height, color)

    # Set labels and title
    ax.set_xlabel('Length (cm)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Width (cm)', fontsize=10, fontweight='bold')
    ax.set_zlabel('Height (cm)', fontsize=10, fontweight='bold')
    ax.set_title(title, fontsize=11, fontweight='bold', pad=5)

    # Set tick params
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.tick_params(axis='z', labelsize=8)

    # CRITICAL: Set true physical aspect ratio for 3D
    ax.set_box_aspect((container_l, container_w, container_h))

    # Set limits
    ax.set_xlim(0, container_l)
    ax.set_ylim(container_w, 0)  # Inverted for proper orientation
    ax.set_zlim(0, container_h)

    # Set view angle
    ax.view_init(elev=elev, azim=azim)


def plot_container_2d_top_connected(ax, container: Container3D,
                                    container_l: float, container_w: float, container_h: float,
                                    title: str):
    """Plot top-down 2D view with connected layout styling."""

    # Draw container outline
    rect = matplotlib.patches.Rectangle((0, 0), container_l, container_w,
                                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    # Draw items
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        rect = matplotlib.patches.Rectangle(
            (placed.x, placed.y), placed.length, placed.width,
            linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
        )
        ax.add_patch(rect)

    # Labels
    ax.set_xlabel('Length (cm)', fontsize=9, fontweight='bold')
    ax.set_ylabel('Width (cm)', fontsize=9, fontweight='bold')
    ax.set_title(title, fontsize=10, fontweight='bold', pad=2)

    # CRITICAL: Equal aspect ratio for true proportions
    ax.set_aspect('equal')

    # Set limits
    ax.set_xlim(-container_l*0.01, container_l*1.01)
    ax.set_ylim(container_w*1.01, -container_w*0.01)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3, linestyle='--')


def plot_container_2d_front_connected(ax, container: Container3D,
                                     container_l: float, container_w: float, container_h: float,
                                     title: str):
    """Plot front 2D view with connected layout styling."""

    # Draw container outline
    rect = matplotlib.patches.Rectangle((0, 0), container_l, container_h,
                                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    # Draw items
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        rect = matplotlib.patches.Rectangle(
            (placed.x, placed.z), placed.length, placed.height,
            linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
        )
        ax.add_patch(rect)

    # Labels
    ax.set_xlabel('Length (cm)', fontsize=9, fontweight='bold')
    ax.set_ylabel('Height (cm)', fontsize=9, fontweight='bold')
    ax.set_title(title, fontsize=10, fontweight='bold', pad=2)

    # CRITICAL: Equal aspect ratio for true proportions
    ax.set_aspect('equal')

    # Set limits
    ax.set_xlim(-container_l*0.01, container_l*1.01)
    ax.set_ylim(container_h*1.01, -container_h*0.01)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3, linestyle='--')


def plot_container_2d_side_connected(ax, container: Container3D,
                                    container_l: float, container_w: float, container_h: float,
                                    title: str):
    """Plot side 2D view with connected layout styling."""

    # Draw container outline
    rect = matplotlib.patches.Rectangle((0, 0), container_w, container_h,
                                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    # Draw items
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        rect = matplotlib.patches.Rectangle(
            (placed.y, placed.z), placed.width, placed.height,
            linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
        )
        ax.add_patch(rect)

    # Labels
    ax.set_xlabel('Width (cm)', fontsize=9, fontweight='bold')
    ax.set_ylabel('Height (cm)', fontsize=9, fontweight='bold')
    ax.set_title(title, fontsize=10, fontweight='bold', pad=2)

    # CRITICAL: Equal aspect ratio for true proportions
    ax.set_aspect('equal')

    # Set limits
    ax.set_xlim(-container_w*0.01, container_w*1.01)
    ax.set_ylim(container_h*1.01, -container_h*0.01)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3, linestyle='--')


def plot_container_2d_top(ax, container: Container3D,
                          container_l: float, container_w: float, container_h: float,
                          title: str):
    """Plot top-down 2D view (X-Y plane)."""

    # Draw container outline
    rect = matplotlib.patches.Rectangle((0, 0), container_l, container_w,
                                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    # Draw items (showing X and Y dimensions)
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        rect = matplotlib.patches.Rectangle(
            (placed.x, placed.y), placed.length, placed.width,
            linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
        )
        ax.add_patch(rect)

    # Set labels and title
    ax.set_xlabel('Length (cm)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Width (cm)', fontsize=10, fontweight='bold')
    ax.set_title(title, fontsize=11, fontweight='bold', pad=5)

    # CRITICAL: Set equal aspect ratio for true physical proportions
    ax.set_aspect('equal')

    # Set limits with some padding
    ax.set_xlim(-container_l*0.02, container_l*1.02)
    ax.set_ylim(container_w*1.02, -container_w*0.02)  # Inverted Y for consistency with 3D
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.3, linestyle='--')


def plot_container_2d_front(ax, container: Container3D,
                            container_l: float, container_w: float, container_h: float,
                            title: str):
    """Plot front 2D view (X-Z plane)."""

    # Draw container outline
    rect = matplotlib.patches.Rectangle((0, 0), container_l, container_h,
                                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    # Draw items (showing X and Z dimensions)
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        rect = matplotlib.patches.Rectangle(
            (placed.x, placed.z), placed.length, placed.height,
            linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
        )
        ax.add_patch(rect)

    # Set labels and title
    ax.set_xlabel('Length (cm)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Height (cm)', fontsize=10, fontweight='bold')
    ax.set_title(title, fontsize=11, fontweight='bold', pad=5)

    # CRITICAL: Set equal aspect ratio for true physical proportions
    ax.set_aspect('equal')

    # Set limits with some padding
    ax.set_xlim(-container_l*0.02, container_l*1.02)
    ax.set_ylim(container_h*1.02, -container_h*0.02)  # Inverted Z for consistency
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.3, linestyle='--')


def plot_container_2d_side(ax, container: Container3D,
                           container_l: float, container_w: float, container_h: float,
                           title: str):
    """Plot side 2D view (Y-Z plane)."""

    # Draw container outline
    rect = matplotlib.patches.Rectangle((0, 0), container_w, container_h,
                                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    # Draw items (showing Y and Z dimensions)
    for placed in container.placed_items:
        color = get_item_color(placed.item.name)
        rect = matplotlib.patches.Rectangle(
            (placed.y, placed.z), placed.width, placed.height,
            linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
        )
        ax.add_patch(rect)

    # Set labels and title
    ax.set_xlabel('Width (cm)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Height (cm)', fontsize=10, fontweight='bold')
    ax.set_title(title, fontsize=11, fontweight='bold', pad=5)

    # CRITICAL: Set equal aspect ratio for true physical proportions
    ax.set_aspect('equal')

    # Set limits with some padding
    ax.set_xlim(-container_w*0.02, container_w*1.02)
    ax.set_ylim(container_h*1.02, -container_h*0.02)  # Inverted Z for consistency
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.3, linestyle='--')


def draw_container_wireframe_3d(ax, l: float, w: float, h: float):
    """Draw container wireframe in 3D."""
    # Bottom face
    ax.plot([0, l, l, 0, 0], [0, 0, w, w, 0], [0, 0, 0, 0, 0], 'k-', linewidth=2, alpha=0.5)
    # Top face
    ax.plot([0, l, l, 0, 0], [0, 0, w, w, 0], [h, h, h, h, h], 'k-', linewidth=2, alpha=0.5)
    # Vertical edges
    ax.plot([0, 0], [0, 0], [0, h], 'k-', linewidth=2, alpha=0.5)
    ax.plot([l, l], [0, 0], [0, h], 'k-', linewidth=2, alpha=0.5)
    ax.plot([l, l], [w, w], [0, h], 'k-', linewidth=2, alpha=0.5)
    ax.plot([0, 0], [w, w], [0, h], 'k-', linewidth=2, alpha=0.5)


def draw_box_3d(ax, x: float, y: float, z: float,
               l: float, w: float, h: float,
               color: str, alpha: float = 0.7):
    """Draw a 3D box with proper faces and edges."""

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
