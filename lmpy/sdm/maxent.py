"""Module containing MaxEnt constants."""
import os
import subprocess


# .....................................................................................
try:
    JAVA_CMD = os.environ['JAVA_CMD']
except KeyError:
    JAVA_CMD = 'java'
try:
    JAVA_OPTS = os.environ['JAVA_OPTIONS']
except KeyError:
    JAVA_OPTS = ''
MAXENT_VERSION = "3.4.4"
MAXENT_JAR = f"/git/Maxent/ArchivedReleases/{MAXENT_VERSION}/maxent.jar"
# MAXENT_JAR = os.environ['MAXENT_JAR']
MAXENT_MODEL_TOOL = 'density.MaxEnt'
MAXENT_PROJECT_TOOL = 'density.Project'
MAXENT_CONVERT_TOOL = 'density.Convert'
# MAXENT_VERSION = os.environ['MAXENT_VERSION']

DEFAULT_MAXENT_OPTIONS = 'nowarnings nocache autorun -z'


# .....................................................................................
def create_maxent_model(
    points_filename,
    layer_dir,
    work_dir='.',
    maxent_arguments=DEFAULT_MAXENT_OPTIONS
):
    """Run Maxent.

    Args:
        points_filename: filename containing occurrence point data
        layer_dir: directory containing environmental layer input
        work_dir:  directory for computations.
        maxent_arguments: parameters for the Maxent program.
    """
    model_command = [JAVA_CMD]
    if len(JAVA_OPTS) > 0:
        model_command.append(JAVA_OPTS)
    model_command.extend(
        [
            '-cp',
            MAXENT_JAR,
            MAXENT_MODEL_TOOL,
            f'samplesfile={points_filename}',
            '-e',
            layer_dir,
            '-o',
            work_dir
        ]
    )

    model_command.extend(maxent_arguments.split(' '))
    subprocess.run(model_command, capture_output=True, check=True)


# .....................................................................................
def project_maxent_model(
    maxent_lambdas_file,
    layer_dir,
    proj_raster_filename
):
    """Project a maxent model onto environmental layers to produce a predicted map.

    Args:
        maxent_lambdas_file: Maxent model file
        layer_dir: directory containing environmental layers to project onto.
        proj_raster_filename: filename for output raster
    """
    project_command = [JAVA_CMD]
    if len(JAVA_OPTS) > 0:
        project_command.append(JAVA_OPTS)
    project_command.extend(
        [
            '-cp',
            MAXENT_JAR,
            MAXENT_PROJECT_TOOL,
            maxent_lambdas_file,
            layer_dir,
            proj_raster_filename
        ]
    )

    subprocess.run(project_command, capture_output=True, check=True)
