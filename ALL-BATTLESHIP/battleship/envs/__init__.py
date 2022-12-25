from gym.envs.registration import register

register(
    id='Battleship-v0',
    entry_point='battleship.envs.gym:MyEnv',
)
