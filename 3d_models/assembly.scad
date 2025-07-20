// Automated Cat Feeder - Complete Assembly
// OpenSCAD file for 3D visualization

// Assembly parameters
base_width = 200;
base_depth = 150;
base_height = 80;
hopper_width = 120;
hopper_depth = 80;
hopper_height = 150;
load_cell_width = 150;
load_cell_depth = 120;
load_cell_height = 20;

// Colors for different components
color_base = [0.9, 0.9, 0.9];      // Light gray
color_hopper = [0.8, 0.8, 0.8];    // Darker gray
color_electronics = [0.2, 0.6, 0.2]; // Green for Pi
color_display = [0.1, 0.1, 0.1];   // Black
color_servo = [0.2, 0.4, 0.8];     // Blue
color_load_cell = [0.7, 0.7, 0.7]; // Silver
color_bowl = [1.0, 1.0, 1.0];      // White
color_food = [0.8, 0.6, 0.4];      // Brown for food

// Main base enclosure
module base_enclosure() {
    color(color_base)
    difference() {
        // Main body
        cube([base_width, base_depth, base_height]);
        
        // Internal cavity
        translate([2, 2, 2])
        cube([base_width - 4, base_depth - 4, base_height - 2]);
        
        // Ventilation holes
        for (x = [15 : 30 : base_width - 15]) {
            for (y = [15 : 30 : base_depth - 15]) {
                translate([x, y, base_height - 2])
                cylinder(h = 3, d = 3, $fn = 20);
            }
        }
        
        // Cable routing holes
        translate([base_width/2, base_depth - 5, base_height/2])
        rotate([90, 0, 0])
        cylinder(h = 10, d = 8, $fn = 20);
        
        translate([base_width - 5, base_depth/2, base_height/2])
        rotate([0, -90, 0])
        cylinder(h = 10, d = 6, $fn = 20);
    }
}

// Food hopper
module food_hopper() {
    color(color_hopper)
    difference() {
        // Main hopper body
        hull() {
            // Top opening
            translate([0, 0, hopper_height])
            cube([hopper_width, hopper_depth, 1]);
            
            // Bottom neck
            translate([(hopper_width - 40)/2, (hopper_depth - 40)/2, 30])
            cube([40, 40, 1]);
        }
        
        // Internal cavity
        translate([2, 2, 2])
        hull() {
            // Top opening
            translate([0, 0, hopper_height - 2])
            cube([hopper_width - 4, hopper_depth - 4, 1]);
            
            // Bottom neck
            translate([(hopper_width - 40)/2 - 2, (hopper_depth - 40)/2 - 2, 30])
            cube([44, 44, 1]);
        }
        
        // Food outlet
        translate([hopper_width/2, hopper_depth/2, 0])
        cylinder(h = 31, d = 25, $fn = 40);
        
        // Servo mounting cutout
        translate([(hopper_width - 22.2)/2, (hopper_depth - 11.8)/2, 30 - 31])
        cube([22.2, 11.8, 31]);
    }
}

// Load cell mounting platform
module load_cell_platform() {
    color(color_base)
    difference() {
        // Main platform
        cube([load_cell_width, load_cell_depth, load_cell_height]);
        
        // Weight reduction cutouts
        for (x = [20 : 30 : load_cell_width - 20]) {
            for (y = [20 : 30 : load_cell_depth - 20]) {
                translate([x, y, -1])
                cylinder(h = load_cell_height + 2, d = 15, $fn = 30);
            }
        }
        
        // Load cell mounting area
        translate([(load_cell_width - 34)/2, (load_cell_depth - 34)/2, load_cell_height])
        cube([34, 34, 3]);
        
        // Bowl support cutout
        translate([(load_cell_width - 100)/2, (load_cell_depth - 100)/2, load_cell_height])
        cylinder(h = 10, d = 100, $fn = 60);
    }
}

// Raspberry Pi
module raspberry_pi() {
    color(color_electronics)
    translate([(base_width - 85)/2, (base_depth - 56)/2, 2])
    difference() {
        cube([85, 56, 15]);
        
        // GPIO header
        translate([21, 3.5, 15])
        cube([51, 5, 2]);
        
        // USB ports
        translate([0, 6, 15])
        cube([15, 8, 2]);
        
        // Power port
        translate([70, 6, 15])
        cube([8, 8, 2]);
    }
}

// LCD Display
module lcd_display() {
    color(color_display)
    translate([(base_width - 80)/2, base_depth - 12, base_height - 46])
    cube([80, 12, 36]);
}

// Servo Motor
module servo_motor() {
    color(color_servo)
    translate([(base_width - 22.2)/2, (base_depth - 11.8)/2, base_height + 30])
    cube([22.2, 11.8, 31]);
}

// Load Cell
module load_cell() {
    color(color_load_cell)
    translate([(base_width - 34)/2, (base_depth - 34)/2, -18])
    cube([34, 34, 7]);
}

// Food Bowl
module food_bowl() {
    color(color_bowl)
    translate([(base_width - 100)/2, (base_depth - 100)/2, -10])
    difference() {
        cylinder(h = 30, d = 100, $fn = 60);
        
        // Bowl cavity
        translate([0, 0, 5])
        cylinder(h = 25, d = 90, $fn = 60);
    }
}

// Cat Food
module cat_food() {
    color(color_food)
    translate([(base_width - 90)/2, (base_depth - 90)/2, -5])
    cylinder(h = 15, d = 90, $fn = 60);
}

// Push Buttons
module push_buttons() {
    color([0.3, 0.3, 0.3])
    for (i = [0:3]) {
        translate([20 + i*25, base_depth - 30, base_height - 25])
        cylinder(h = 5, d = 15, $fn = 20);
    }
}

// Status LED
module status_led() {
    color([1, 0, 0])  // Red LED
    translate([base_width - 40, base_depth - 30, base_height - 25])
    cylinder(h = 5, d = 5, $fn = 20);
}

// Mounting Brackets
module mounting_brackets() {
    color(color_base)
    // Front bracket
    translate([0, -10, 0])
    cube([base_width, 10, 2]);
    
    // Back bracket
    translate([0, base_depth, 0])
    cube([base_width, 10, 2]);
    
    // Mounting holes
    for (x = [20, base_width - 20]) {
        // Front holes
        translate([x, -5, 1])
        rotate([90, 0, 0])
        cylinder(h = 15, d = 4, $fn = 20);
        
        // Back holes
        translate([x, base_depth + 5, 1])
        rotate([-90, 0, 0])
        cylinder(h = 15, d = 4, $fn = 20);
    }
}

// Complete assembly
module complete_assembly() {
    // Base enclosure
    base_enclosure();
    
    // Mounting brackets
    mounting_brackets();
    
    // Food hopper (mounted on top)
    translate([(base_width - hopper_width)/2, (base_depth - hopper_depth)/2, base_height])
    food_hopper();
    
    // Load cell platform (mounted below)
    translate([(base_width - load_cell_width)/2, (base_depth - load_cell_depth)/2, -load_cell_height])
    load_cell_platform();
    
    // Electronics
    raspberry_pi();
    lcd_display();
    servo_motor();
    load_cell();
    
    // User interface
    push_buttons();
    status_led();
    
    // Food bowl and contents
    food_bowl();
    cat_food();
}

// Render the complete assembly
complete_assembly();

// Optional: Add a cat silhouette for scale reference
module cat_silhouette() {
    color([0.2, 0.2, 0.2])
    translate([base_width + 20, base_depth/2, 0])
    scale([0.5, 0.5, 1])
    union() {
        // Cat body
        translate([0, 0, 20])
        cylinder(h = 40, d = 30, $fn = 30);
        
        // Cat head
        translate([15, 0, 50])
        sphere(d = 20, $fn = 30);
        
        // Cat ears
        translate([20, -8, 60])
        rotate([0, 0, 30])
        cylinder(h = 10, d = 8, $fn = 20);
        
        translate([20, 8, 60])
        rotate([0, 0, -30])
        cylinder(h = 10, d = 8, $fn = 20);
        
        // Cat tail
        translate([-15, 0, 30])
        rotate([0, 90, 0])
        cylinder(h = 20, d = 8, $fn = 20);
    }
}

// Uncomment to add cat silhouette
// cat_silhouette(); 