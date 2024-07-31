from krave.experiment.task import Task


if __name__ == '__main__':
    Task(mouse="test",
         rig_name="rig1",
         training="regular",
         trainer="Rebekah").run()
