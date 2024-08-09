from krave.experiment.task import Task    

if __name__ == '__main__':
    Task(mouse="RZ045",
         rig_name="rig3",
         training="regular",
         trainer="Rebekah",
         record=False,
         forward_file = False).run()
