import jinja2
import os

from zppy.utils import (
    checkStatus,
    getComponent,
    getTasks,
    getYears,
    submitScript,
)

# -----------------------------------------------------------------------------
def e3sm_chem_diags(path, config, scriptDir, existing_bundles, job_ids_file):

    # Initialize jinja2 template engine
    path_extra = os.path.join(path,"templates")
    templateLoader = jinja2.FileSystemLoader(
        searchpath=(config["default"]["templateDir"], path_extra)
    )
    templateEnv = jinja2.Environment( loader=templateLoader )

    # --- List of e3sm_chem_diags tasks ---
    tasks = getTasks(config, 'e3sm_chem_diags')
    if (len(tasks) == 0):
        return existing_bundles

    # --- Generate and submit e3sm_diags scripts ---
    for c in tasks:

        if 'ts_num_years' in c.keys():
          c['ts_num_years'] = int(c['ts_num_years'])

        # Component
         # c['component'] = getComponent(c['input_files'])
         # c['component2'] = getComponent(c['input_files2'])

        # Loop over year sets
        year_sets = getYears(c['years'])
        for s in year_sets:
            c['year1'] = s[0]
            c['year2'] = s[1]
            c['ypf'] = s[1] - s[0] + 1
            c['scriptDir'] = scriptDir
            if c['subsection'] == "ts_diags":
                sub = c['subsection']
                prefix = 'chem_%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_chem_diags_ts.bash' )
            elif c['subsection'] == "o3_hole_diags":
                sub = c['subsection']
                prefix = '%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'o3_hole_diags.bash' )
            elif c['subsection'] == "TOZ_eq_native":
                sub = c['subsection']
                prefix = '%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'TOZ_eq_plot.bash' )
            elif c['subsection'] == "surf_o3_diags":
                sub = c['subsection']
                prefix = '%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'surf_o3_diags.bash' )
            elif c['subsection'] == "STE_flux_native":
                sub = c['subsection']
                prefix = '%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'STE_flux_diags.bash' )
            elif c['subsection'] == "temperature_eq_native":
                sub = c['subsection']
                prefix = '%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'temperature_eq_plot.bash' )
            elif c['subsection'] == "summary_table_native":
                sub = c['subsection']
                prefix = '%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'chem_summary_table.bash' )
            elif c['subsection'] == "cmip_comparison":
                sub = c['subsection']
                prefix = 'chem_%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_chem_cmip_comparison.bash' )
            elif c['subsection'] == "noaa_co_comparison":
                sub = c['subsection']
                prefix = 'chem_%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_chem_noaa_co_comparison.bash' )
            elif c['subsection'] == "pres_lat_plots":
                sub = c['subsection']
                prefix = 'e3sm_%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_pres_lat_plots.bash' )
            elif c['subsection'] == "lat_lon_plots":
                sub = c['subsection']
                prefix = 'e3sm_%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_lat_lon_plots.bash' )
            elif c['subsection'] == "nox_emis_plots":
                sub = c['subsection']
                prefix = 'e3sm_%s_%04d-%04d' % (sub,c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_nox_emis_plots.bash' )
            elif c['subsection'] == "index":
                prefix = 'e3sm_chem_index'
                template = templateEnv.get_template( 'e3sm_chem_index.bash' )
            else:
                sub = c['grid']
                prefix = 'e3sm_chem_diags_%04d-%04d' % (c['year1'],c['year2'])
                template = templateEnv.get_template( 'e3sm_chem_diags.bash' )
            c['prefix'] = prefix
            scriptFile = os.path.join(scriptDir, '%s.bash' % (prefix))
            statusFile = os.path.join(scriptDir, '%s.status' % (prefix))
            skip = checkStatus(statusFile)
            if skip:
                continue

            # Create script
            with open(scriptFile, 'w') as f:
                f.write(template.render( **c ))

            # List of depensencies
            export = 'NONE'
            if c['subsection'] == "cmip_comparison":
                dependencies = [ os.path.join(scriptDir, 'ts_atm_monthly_180x360_aave_%04d-%04d-%04d.status' % (c['year1'],c['year2'],c['ypf'])), ]
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            elif c['subsection'] == "noaa_co_comparison":
                dependencies = [ os.path.join(scriptDir, 'ts_atm_monthly_180x360_aave_%04d-%04d-%04d.status' % (c['year1'],c['year2'],c['ypf'])), ]
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            elif c['subsection'] == "surf_o3_diags":
                dependencies = [ os.path.join(scriptDir, 'ts_atm_hourly_US1.0x1.0_nco_%04d-%04d-%04d.status' % (c['year1'],c['year2'],c['ypf'])), ] 
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            elif c['subsection'] == "climo_diags":
                dependencies = [ os.path.join(scriptDir, 'climo_native_aave_%04d-%04d.status' % (c['year1'],c['year2'])), ]
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            elif c['subsection'] == "pres_lat_plots":
                dependencies = [ os.path.join(scriptDir, 'climo_180x360_aave_%04d-%04d.status' % (c['year1'],c['year2'])), ]
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            elif c['subsection'] == "lat_lon_plots":
                dependencies = [ os.path.join(scriptDir, 'climo_180x360_aave_%04d-%04d.status' % (c['year1'],c['year2'])), ]
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            elif c['subsection'] == "nox_emis_plots":
                dependencies = [ os.path.join(scriptDir, 'climo_180x360_aave_%04d-%04d.status' % (c['year1'],c['year2'])), ]
                submitScript(scriptFile, statusFile, export, job_ids_file, dependFiles=dependencies)
            else:
                submitScript(scriptFile, statusFile, export, job_ids_file)

    return existing_bundles
