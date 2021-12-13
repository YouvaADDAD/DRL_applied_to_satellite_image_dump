from    sat_env import  *


def glouton_test_env(nbsats,nbstations):
  env=SatEnv(nbsats,nbstations)
  score = 0
  step = 0
  for x in range(1):
      env.reset()
      done = False
      while not done:
          obs=env.observation_space
          decision=bool(obs[0]) or obs[3]>0.75 or obs[-6] > 1.0 or obs[14]<9000 or obs[8]<8000 or obs[11]<1000 
          status,reward,done,_=env.step(int(decision))
          score+=reward
          step+=1

      print("reward : ", score/step, "Pertincence Score completed", env.positifReward())


