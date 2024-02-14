import logging

import ctk
import qt
import slicer
import vtk
import vtk.util.numpy_support as vtk_np
from slicer.ScriptedLoadableModule import *

import numpy as np

import SampleData

# Rename "YourName" everywhere in this file to your first and last name. Also rename this file and its folder.
# You'll have to do the widget connections in ProgrammingAssignmentMarcoLudwigWidget.
# Do your work in the method ProgrammingAssignmentMarcoLudwigLogic.run.


class ProgrammingAssignmentMarcoLudwig(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:

    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        applicant_name = "Marco Ludwig"
        self.parent.title = "Programming Assignment: {}".format(applicant_name)
        self.parent.categories = ["Programming Assignment"]
        self.parent.dependencies = []
        self.parent.contributors = [applicant_name]
        self.parent.helpText = ""
        self.parent.acknowledgementText = ""


class ProgrammingAssignmentMarcoLudwigWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:

    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def onApllyButton(self):
        input = self.input_selector.currentNode()
        output = self.output_selector.currentNode()
        threshold = self.image_threshold_slider_vidget.value

        if self.logic.run(input, output, threshold):
            slicer.util.infoDisplay("Threshold operation completed!")

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...
        self.logic = ProgrammingAssignmentMarcoLudwigLogic()

        #
        # Parameters Area
        #
        parameters_collapsible_button = ctk.ctkCollapsibleButton()
        parameters_collapsible_button.text = "Parameters"
        self.layout.addWidget(parameters_collapsible_button)

        # Layout within the dummy collapsible button
        parameters_form_layout = qt.QFormLayout(parameters_collapsible_button)

        #
        # input volume selector
        #
        self.input_selector = slicer.qMRMLNodeComboBox()
        self.input_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.input_selector.selectNodeUponCreation = True
        self.input_selector.addEnabled = False
        self.input_selector.removeEnabled = False
        self.input_selector.noneEnabled = False
        self.input_selector.showHidden = False
        self.input_selector.showChildNodeTypes = False
        self.input_selector.setMRMLScene(slicer.mrmlScene)
        self.input_selector.setToolTip("Pick the input to the algorithm.")
        parameters_form_layout.addRow("Input Volume: ", self.input_selector)

        #
        # output volume selector
        #
        self.output_selector = slicer.qMRMLNodeComboBox()
        self.output_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.output_selector.selectNodeUponCreation = True
        self.output_selector.addEnabled = True
        self.output_selector.renameEnabled = True
        self.output_selector.removeEnabled = True
        self.output_selector.noneEnabled = False
        self.output_selector.showHidden = False
        self.output_selector.showChildNodeTypes = False
        self.output_selector.setMRMLScene(slicer.mrmlScene)
        self.output_selector.setToolTip("Pick the output to the algorithm.")
        parameters_form_layout.addRow("Output Volume: ", self.output_selector)

        #
        # threshold value
        #
        self.image_threshold_slider_vidget = ctk.ctkSliderWidget()
        self.image_threshold_slider_vidget.singleStep = 0.01
        self.image_threshold_slider_vidget.minimum = 0.0
        self.image_threshold_slider_vidget.maximum = 100
        self.image_threshold_slider_vidget.value = 0.5
        parameters_form_layout.addRow(
            "Image threshold", self.image_threshold_slider_vidget
        )

        #
        # Apply Button
        #
        self.apply_button = qt.QPushButton("Apply")
        self.apply_button.toolTip = "Run the algorithm."
        self.apply_button.enabled = True
        parameters_form_layout.addRow(self.apply_button)

        # connections
        self.apply_button.connect("clicked()", self.onApllyButton)

        # Add vertical spacer
        self.layout.addStretch(1)


class ProgrammingAssignmentMarcoLudwigLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual computation done by your module.

    The interface should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def has_image_data(self, volume_node):
        """This is an example logic method that returns true if the passed in volume node has valid image data"""
        if not volume_node:
            logging.debug("has_image_data failed: no volume node")
            return False
        if volume_node.GetImageData() is None:
            logging.debug("has_image_data failed: no image data in volume node")
            return False
        return True

    def is_valid_input_output_data(self, input_volume_node, output_volume_node):
        """Validates if the output is not the same as input"""

        if not input_volume_node:
            logging.debug(
                "is_valid_input_output_data failed: no input volume node defined"
            )
            return False

        if not output_volume_node:
            logging.debug(
                "is_valid_input_output_data failed: no output volume node defined"
            )
            return False

        if input_volume_node.GetID() == output_volume_node.GetID():
            logging.debug(
                "is_valid_input_output_data failed: input and output volume is the same. Create a new volume for "
                "output to avoid this error."
            )
            return False
        return True

    def run(self, input_volume, output_volume, image_threshold):
        """Run the actual algorithm"""

        if not self.is_valid_input_output_data(input_volume, output_volume):
            slicer.util.errorDisplay(
                "Input volume is the same as output volume. Choose a different output volume."
            )
            return False

        if not self.has_image_data(input_volume):
            return False
        #######################################################################
        #                     run threshold algorithm here                    #
        #######################################################################

        input_data = input_volume.GetImageData()
        input_array = vtk_np.vtk_to_numpy(input_data.GetPointData().GetScalars())
        img_threshold = input_array
        img_threshold[input_array < image_threshold] = 0

        output_data = vtk.vtkImageData()
        output_data.SetDimensions(input_data.GetDimensions())
        output_data.GetPointData().SetScalars(
            vtk_np.numpy_to_vtk(num_array=img_threshold, deep=0, array_type=None)
        )

        output_volume.SetAndObserveImageData(output_data)

        return True


class ProgrammingAssignmentMarcoLudwigTest(ScriptedLoadableModuleTest):
    """This is the test case for your scripted module.

    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_Skeleton1()

    def test_Skeleton1(self):
        input_volume = SampleData.downloadSample("MRHead")
        output_volume = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLScalarVolumeNode", "test_node"
        )

        logic = ProgrammingAssignmentMarcoLudwigLogic()

        self.assertFalse(logic.run(input_volume, input_volume, 100))
