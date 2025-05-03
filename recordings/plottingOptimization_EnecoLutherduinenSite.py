from topfarm.recorders import TopFarmListRecorder
import matplotlib.pyplot as plt
# recorder = TopFarmListRecorder().load('/Users/rafaelvalottarodrigues/Documents/software/farm_to_farm_bench/recordings/optimization_viveyard.pkl')
recorder = TopFarmListRecorder().load(r'E:\Spring 2025\ENGIN 480\Porject_4\Project_4_Engin_480_kalogeras_Trin\recordings\optimization_EnecoLutherduinenSite.pkl')
# '/Users/rafaelvalottarodrigues/Documents/software/farm_to_farm_bench/recordings/
# optimization_borselle.pkl'
plt.figure()
plt.plot(recorder['counter'], recorder['AEP']/recorder['AEP'][-1])
plt.xlabel('Iterations')
plt.ylabel('AEP/AEP_opt')
plt.title('Optimization Progress: Eneco Luchterduinen Site')
plt.show()
print('done')
