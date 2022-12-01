"""Experimental Block object."""


class BlockDefault:
    def __init__(self, session_config, block_config):
        self.block_length = session_config["block_length"]
        self.reward_consumption_time = session_config["reward_consumption_time"]
        self.reward_distribution = self.get_reward_distribution(session_config)
        self.id = block_config["id"]
        self.bg_reward_rate = block_config["bg_reward_rate"]

    def run(self, water, lick, visual, data_saver):
        """Run block."""
        for trial in self.block_length:
            visual.cue_on()
            while not lick.status_change:
                continue
            water.reward(self.reward_distribution)
            water.consumption()
            water.ITI()


class BlockExp2:
    def __init__(self, session_config, block_config):
        self.block_length = session_config["block_length"]
        self.reward_consumption_time = session_config["reward_consumption_time"]
        self.reward_distribution = self.get_reward_distribution(session_config)
        self.id = block_config["id"]
        self.bg_reward_rate = block_config["bg_reward_rate"]

    def run(self, water, lick, visual, data_saver):
        """Run block."""
        for trial in self.block_length:
            visual.cue()
            while not lick.status_change:
                continue
            water.reward(self.reward_distribution)
            water.consumption()
            water.ITI()