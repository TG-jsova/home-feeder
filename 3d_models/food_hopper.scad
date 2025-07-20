// Automated Cat Feeder - Food Hopper
// OpenSCAD file for 3D printing

// Parameters
hopper_width = 120;
hopper_depth = 80;
hopper_height = 150;
wall_thickness = 2;
neck_width = 40;
neck_height = 30;
outlet_diameter = 25;

// Servo mounting
servo_width = 22.2;
servo_depth = 11.8;
servo_height = 31;
servo_mount_thickness = 3;

module main_hopper() {
    difference() {
        // Main hopper body
        hull() {
            // Top opening
            translate([0, 0, hopper_height])
            cube([hopper_width, hopper_depth, 1]);
            
            // Bottom neck
            translate([(hopper_width - neck_width)/2, (hopper_depth - neck_width)/2, neck_height])
            cube([neck_width, neck_width, 1]);
        }
        
        // Internal cavity
        translate([wall_thickness, wall_thickness, wall_thickness])
        hull() {
            // Top opening
            translate([0, 0, hopper_height - wall_thickness])
            cube([hopper_width - 2*wall_thickness, hopper_depth - 2*wall_thickness, 1]);
            
            // Bottom neck
            translate([(hopper_width - neck_width)/2 - wall_thickness, (hopper_depth - neck_width)/2 - wall_thickness, neck_height])
            cube([neck_width + 2*wall_thickness, neck_width + 2*wall_thickness, 1]);
        }
        
        // Food outlet
        translate([hopper_width/2, hopper_depth/2, 0])
        cylinder(h = neck_height + 1, d = outlet_diameter, $fn = 40);
        
        // Servo mounting cutout
        translate([(hopper_width - servo_width)/2, (hopper_depth - servo_depth)/2, neck_height - servo_height])
        cube([servo_width, servo_depth, servo_height + 1]);
    }
}

module servo_mount() {
    // Servo mounting bracket
    translate([(hopper_width - servo_width - 10)/2, (hopper_depth - servo_depth - 10)/2, neck_height - servo_height - servo_mount_thickness])
    difference() {
        cube([servo_width + 10, servo_depth + 10, servo_mount_thickness]);
        
        // Servo mounting holes
        translate([5, 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        translate([servo_width + 5, 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        translate([5, servo_depth + 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        translate([servo_width + 5, servo_depth + 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        // Servo body cutout
        translate([5, 5, -1])
        cube([servo_width, servo_depth, servo_mount_thickness + 2]);
    }
}

module food_gate() {
    gate_width = outlet_diameter + 10;
    gate_height = 8;
    gate_depth = 3;
    
    // Gate arm
    translate([(hopper_width - gate_width)/2, hopper_depth/2 - gate_depth/2, neck_height - gate_height])
    difference() {
        cube([gate_width, gate_depth, gate_height]);
        
        // Servo arm attachment hole
        translate([gate_width/2, gate_depth/2, gate_height/2])
        rotate([90, 0, 0])
        cylinder(h = gate_depth + 2, d = 2, $fn = 20);
    }
}

module mounting_flange() {
    flange_width = hopper_width + 20;
    flange_depth = hopper_depth + 20;
    flange_height = 5;
    
    translate([-10, -10, 0])
    difference() {
        cube([flange_width, flange_depth, flange_height]);
        
        // Mounting holes
        for (x = [15, flange_width - 15]) {
            for (y = [15, flange_depth - 15]) {
                translate([x, y, -1])
                cylinder(h = flange_height + 2, d = 4, $fn = 20);
            }
        }
        
        // Center cutout for hopper
        translate([10, 10, -1])
        cube([hopper_width, hopper_depth, flange_height + 2]);
    }
}

module lid() {
    lid_width = hopper_width + 10;
    lid_depth = hopper_depth + 10;
    lid_height = 5;
    
    translate([-5, -5, hopper_height])
    difference() {
        cube([lid_width, lid_depth, lid_height]);
        
        // Handle cutout
        translate([lid_width/2 - 15, lid_depth/2 - 5, lid_height - 3])
        cube([30, 10, 4]);
        
        // Ventilation holes
        for (x = [10 : 20 : lid_width - 10]) {
            for (y = [10 : 20 : lid_depth - 10]) {
                translate([x, y, -1])
                cylinder(h = lid_height + 2, d = 3, $fn = 20);
            }
        }
    }
}

// Main assembly
main_hopper();
servo_mount();
food_gate();
mounting_flange();

// Uncomment to render lid separately
// lid(); 