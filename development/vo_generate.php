<?php

// yuck, it's a commandline php file!
// This will open the YAML file and output the appropriate gamesounds file, generating VCDs if asked.

// vo_generate.php <yaml database>

print "\nvo_generate.php loaded.\n";

if ( $argc != 2 )
    die("Format: vo_generate.php <database_name>\n");

require_once "vo_internal/spyc.php";

// Sniped from http://snipplr.com/view/285/
function wavDur($file) {
    $fp = fopen($file, 'r');
    if (fread($fp,4) == "RIFF") {
    fseek($fp, 20);
    $rawheader = fread($fp, 16);
    $header = unpack('vtype/vchannels/Vsamplerate/Vbytespersec/valignment/vbits',$rawheader);
    $pos = ftell($fp);
    while (fread($fp,4) != "data" && !feof($fp)) {
      $pos++;
      fseek($fp,$pos);
    }
    $rawheader = fread($fp, 4);
    $data = unpack('Vdatasize',$rawheader);
    $sec = $data['datasize']/$header['bytespersec'];
    return round($sec,6);
    }
}

$root_path = substr( getcwd(), 0, strrpos(getcwd(),"\\"));
$database_name = $argv[1];

print "Root Path: ".$root_path."\n\n";

$yaml_file = getcwd()."/vo_databases/".$database_name.".yaml";

if ( !file_exists($yaml_file) )
    die("Unable to read database ".$database_name);

print "Loading YAML database...\n";

$yaml_array = Spyc::YAMLLoad( $yaml_file );

if ( !isset( $yaml_array["settings"]["output"] ) )
    die("Failed loading YAML, settings/output not defined?");

print "Loading templates...\n\n";

if ( !file_exists( "vo_internal/base.template.txt" ) )
    die("Failed loading gamesounds template.");

if ( !file_exists( "vo_internal/base.template.vcd" ) )
    die("Failed loading VCD template.");

$template_gamesounds = file_get_contents( "vo_internal/base.template.txt" );
$template_vcd = file_get_contents( "vo_internal/base.template.vcd" );

print "Generating scripts/".$yaml_array["settings"]["output"].".txt\n";

$soundscript_output = $template_gamesounds;

foreach ( $yaml_array["sounds"] as $title=>$cur_sound )
{
	//var_dump($cur_sound);
    if ( !$cur_sound["category"] || !$yaml_array["categories"][$cur_sound["category"]])
        die("Invalid category for ".$title);
		
	$multiple_sounds = isset($cur_sound["waves"]);

    $generate_vcd = isset($cur_sound["vcd"]) && $cur_sound["vcd"] && !$multiple_sounds;
    $category = $yaml_array["categories"][$cur_sound["category"]];
	
	if ( !$multiple_sounds )
	{
		$vcd_path = "/scenes/".str_replace(".wav",".vcd",$cur_sound["wave"]);
		$vcd_ss_string = ( $generate_vcd ? "// VCD generated in {$vcd_path}" : "" );
		
		$soundscript_output .=
	"
	\"{$title}\" {$vcd_ss_string}
	{
	\t\"channel\" \"{$category['channel']}\"
	\t\"volume\" \"{$category['volume']}\"
	\t\"pitch\" \"{$category['pitch']}\"
	\t\"soundlevel\" \"{$category['soundlevel']}\"

	\t\"wave\" \"{$cur_sound["wave_prefix"]}{$cur_sound["wave"]}\"
	}
	";
	}
	else
	{
		$soundscript_output .=
	"
	\"{$title}\" 
	{
	\t\"channel\" \"{$category['channel']}\"
	\t\"volume\" \"{$category['volume']}\"
	\t\"pitch\" \"{$category['pitch']}\"
	\t\"soundlevel\" \"{$category['soundlevel']}\"
	
		\"rndwave\"
		{
		";	
	
	foreach( $cur_sound["waves"] as $thiswave )
	{
		$soundscript_output .= "\t\"wave\"\t\"{$cur_sound["wave_prefix"]}{$thiswave}\"
		";
	}
	
	$soundscript_output .=
	"}
	}
	";
	}
}

$fh = fopen($root_path."/scripts/".$yaml_array["settings"]["output"].".txt", 'w') or die("can't open file");
fwrite($fh, $soundscript_output);
fclose($fh);

print "Generated scripts/".$yaml_array["settings"]["output"].".txt\n\n";

print "Generating VCDs\n";

foreach ( $yaml_array["sounds"] as $title=>$cur_sound )
{
    $generate_vcd = isset($cur_sound["vcd"]) && $cur_sound["vcd"];

    if ( !$generate_vcd )
        continue;

    $vcd_path = "/scenes/".str_replace(".wav",".vcd",$cur_sound["wave"]);
    $vcd_path_base = substr( $root_path.$vcd_path, 0, strrpos($root_path.$vcd_path,"/") );
    $wave_duration = wavDur( $root_path."/sound/".$cur_sound["wave"] ) or die("Failed calculating WAV duration for ".$cur_sound["wave"]);
    $vcd_output = str_replace( "%SOUND_NAME%", $title, $template_vcd );
    $vcd_output = str_replace( "%SOUND_DURATION%", $wave_duration, $vcd_output );

    if ( !is_dir( $vcd_path_base ) )
        mkdir( $vcd_path_base );

    $fh = fopen($root_path.$vcd_path, 'w') or die("can't open file");
    fwrite($fh, $vcd_output);
    fclose($fh);

    print "Saved ".$vcd_path."\n";
    
}

print "Generated VCDs\n";
print "Done!\n";

?>