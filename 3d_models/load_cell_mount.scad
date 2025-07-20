// Automated Cat Feeder - Load Cell Mount
// OpenSCAD file for 3D printing

// Parameters
base_width = 150;
base_depth = 120;
base_height = 20;
wall_thickness = 3;

// Load cell dimensions
load_cell_width = 34;
load_cell_depth = 34;
load_cell_height = 7;
load_cell_hole_diameter = 3.2;

// Food bowl dimensions
bowl_diameter = 100;
bowl_height = 30;
bowl_rim_width = 5;

// Mounting holes
mount_hole_diameter = 4;
mount_hole_spacing = 120;

module base_plate() {
    difference() {
        // Main base plate
        cube([base_width, base_depth, base_height]);
        
        // Weight reduction cutouts
        for (x = [20 : 30 : base_width - 20]) {
            for (y = [20 : 30 : base_depth - 20]) {
                translate([x, y, -1])
                cylinder(h = base_height + 2, d = 15, $fn = 30);
            }
        }
        
        // Cable routing holes
        translate([base_width/2, base_depth - 10, base_height/2])
        rotate([90, 0, 0])
        cylinder(h = 20, d = 8, $fn = 20);
        
        translate([base_width - 10, base_depth/2, base_height/2])
        rotate([0, -90, 0])
        cylinder(h = 20, d = 6, $fn = 20);
    }
}

module load_cell_mount() {
    // Load cell mounting bracket
    translate([(base_width - load_cell_width - 20)/2, (base_depth - load_cell_depth - 20)/2, base_height])
    difference() {
        cube([load_cell_width + 20, load_cell_depth + 20, wall_thickness]);
        
        // Load cell mounting holes
        translate([10, 10, -1])
        cylinder(h = wall_thickness + 2, d = load_cell_hole_diameter, $fn = 20);
        
        translate([load_cell_width + 10, 10, -1])
        cylinder(h = wall_thickness + 2, d = load_cell_hole_diameter, $fn = 20);
        
        translate([10, load_cell_depth + 10, -1])
        cylinder(h = wall_thickness + 2, d = load_cell_hole_diameter, $fn = 20);
        
        translate([load_cell_width + 10, load_cell_depth + 10, -1])
        cylinder(h = wall_thickness + 2, d = load_cell_hole_diameter, $fn = 20);
        
        // Load cell body cutout
        translate([10, 10, -1])
        cube([load_cell_width, load_cell_depth, wall_thickness + 2]);
        
        // Cable routing
        translate([load_cell_width/2 + 10, load_cell_depth + 10, wall_thickness/2])
        rotate([90, 0, 0])
        cylinder(h = 20, d = 4, $fn = 20);
    }
}

module bowl_support() {
    // Bowl support ring
    translate([(base_width - bowl_diameter)/2, (base_depth - bowl_diameter)/2, base_height + wall_thickness])
    difference() {
        cylinder(h = 10, d = bowl_diameter + 10, $fn = 60);
        
        // Bowl cutout
        translate([0, 0, -1])
        cylinder(h = 12, d = bowl_diameter, $fn = 60);
        
        // Support ribs
        for (angle = [0 : 45 : 315]) {
            rotate([0, 0, angle])
            translate([0, -2, -1])
            cube([bowl_diameter/2, 4, 12]);
        }
        
        // Drainage holes
        for (angle = [0 : 30 : 330]) {
            rotate([0, 0, angle])
            translate([bowl_diameter/3, 0, -1])
            cylinder(h = 12, d = 3, $fn = 20);
        }
    }
}

module mounting_brackets() {
    // Front mounting bracket
    translate([0, -15, 0])
    cube([base_width, 15, base_height]);
    
    // Back mounting bracket
    translate([0, base_depth, 0])
    cube([base_width, 15, base_height]);
    
    // Mounting holes
    for (x = [mount_hole_spacing/2, base_width - mount_hole_spacing/2]) {
        // Front holes
        translate([x, -7.5, base_height/2])
        rotate([90, 0, 0])
        cylinder(h = 15, d = mount_hole_diameter, $fn = 20);
        
        // Back holes
        translate([x, base_depth + 7.5, base_height/2])
        rotate([-90, 0, 0])
        cylinder(h = 15, d = mount_hole_diameter, $fn = 20);
    }
}

module strain_relief() {
    // Cable strain relief
    translate([base_width - 15, base_depth/2, base_height/2])
    rotate([0, -90, 0])
    difference() {
        cylinder(h = 20, d = 12, $fn = 30);
        
        translate([0, 0, -1])
        cylinder(h = 22, d = 8, $fn = 30);
        
        // Cable slot
        translate([-6, -1, -1])
        cube([12, 2, 22]);
    }
}

module leveling_feet() {
    // Leveling feet for stability
    for (x = [10, base_width - 10]) {
        for (y = [10, base_depth - 10]) {
            translate([x, y, -5])
            difference() {
                cylinder(h = 5, d = 15, $fn = 30);
                
                translate([0, 0, -1])
                cylinder(h = 7, d = 8, $fn = 20);
            }
        }
    }
}

// Main assembly
base_plate();
load_cell_mount();
bowl_support();
mounting_brackets();
strain_relief();
leveling_feet(); 