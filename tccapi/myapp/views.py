# gymbroapi/views.py
import os

import joblib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TrainingDataSerializer
import numpy as np
import pandas as pd
import math
from pulp import *

class TrainingPredictionView(APIView):
    def post(self, request, format=None):
        serializer = TrainingDataSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            age = data['age']
            gender = data['gender']
            training_days = data['training_days']
            training_duration = data['training_duration']
            gym_experience = data['gym_experience']
            is_natural = data['is_natural']

            # Chame seu modelo de IA aqui
            prediction = self.predict_training_plan(
                age, gender, training_days, training_duration, gym_experience, is_natural
            )
            return Response({'prediction': prediction}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def predict_training_plan(self, age, gender, training_days, training_duration, gym_experience, is_natural):
        duration = training_duration
        if(training_duration <= 30):
            training_duration = 0
        elif(training_duration > 30 and training_duration <= 60):
            training_duration = 1
        elif(training_duration > 60 and training_duration <= 90):
            training_duration = 2
        elif(training_duration > 90 and training_duration <= 120):
            training_duration = 3
        else:
            training_duration = 4

        if(gym_experience <= 2):
            gym_experience = 0
        elif(gym_experience > 2 and gym_experience <= 5):
            gym_experience = 1
        elif(gym_experience > 5):
            gym_experience = 2

        is_natural = 1 if is_natural == True else 0

        input_data = np.array([[age, gender, training_days-1, training_duration, gym_experience, is_natural]])

        path = os.path.join(os.getcwd(), 'myapp/static/models')
        modelsPath = os.listdir(path)

        a = []
        b = []
        c = []
        d = []
        e = []
        f = []
        g = []


        for modelPath in modelsPath:
            model = joblib.load(f'{path}/{modelPath}')
            predict = model.predict(input_data)
            modelPath = modelPath[:-4]
            if(predict[0] == 1):
                muscleDay = modelPath.split('_')
                if(muscleDay[1] == 'A'):
                    a.append(muscleDay[0])
                elif(muscleDay[1] == 'B'):
                    b.append(muscleDay[0])
                elif (muscleDay[1] == 'C'):
                    c.append(muscleDay[0])
                elif (muscleDay[1] == 'D'):
                    d.append(muscleDay[0])
                elif (muscleDay[1] == 'E'):
                    e.append(muscleDay[0])
                elif (muscleDay[1] == 'F'):
                    f.append(muscleDay[0])
                elif (muscleDay[1] == 'G'):
                    g.append(muscleDay[0])

        print("a:",a)
        print("b:",b)
        print("c:", c)
        print("d:", d)
        print("e:", e)
        print("f:",f)
        print("g:", g)
        return self.solverPO([a, b, c, d, e, f, g], duration, training_days)

    def lenDays(self, division):
        days = 0
        for day in division:
            if(len(day)> 0):
                days+=1
        return days
    def grantedDaysAmount(self, division, training_days):
        days = self.lenDays(division)
        print(f"Days: {days}\n\tTraining days: {training_days}")
        while(days > training_days):
            arrayAux = min(division, key=len)
            division.remove(arrayAux)
            otherArray = min(division, key=len)
            otherArray.extend(arrayAux)
            days = self.lenDays(division)
        while(days < training_days):
            newArray = []
            for i in range(3):
                newArray.append(max(division, key=len)[-1])
                del max(division, key=len)[-1]
            division.append(newArray)
            days = self.lenDays(division)
        for i in division:
            print(i)
        return [set(sublist) for sublist in division]

    def solverPO(self, division, duration, training_days):
        division = self.grantedDaysAmount(division, training_days)
        exercise_train = {}
        path = os.path.join(os.getcwd(), 'myapp/static/solverpo')
        exercises = pd.read_csv(f'{path}/exercises.csv')
        duration_exercise = 130
        maxSeriesByMuscleGroup = 12
        minSeriesByMuscleGroup = 0
        maxSeriesByExercise = 4

        muscleGroup = set(exercises['Muscle Group'])

        for i in range(len(division)):
            for muscle_group in division[i]:
                if i not in exercise_train:
                    exercise_train[i] = {}
                if muscle_group not in exercise_train[i]:
                    exercise_train[i][muscle_group] = {}
                group_exercises = exercises.loc[exercises['Muscle Group'] == muscle_group]['Exercise'].tolist()
                for exercise in group_exercises:
                    exercise_train[i][muscle_group][exercise] = 0

        """
        O exercise_train vai formar uma estrutura similar a um json, um dicionário com a seguinte forma:
        {
            0: {
                "1º grupo muscular para treinar no dia 0":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 0":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 0":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            },
            1: {
                "1º grupo muscular para treinar no dia 1":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 1":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 1":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            },
            2: {
                "1º grupo muscular para treinar no dia 2":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 2":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 2":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            },
            3: {
                "1º grupo muscular para treinar no dia 3":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 3":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 3":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            },
            4: {
                "1º grupo muscular para treinar no dia 4:{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 4":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 4":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            },
            5: {
                "1º grupo muscular para treinar no dia 5":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 5":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 5":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            },
            6: {
                "1º grupo muscular para treinar no dia 6":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "2º grupo muscular para treinar no dia 6":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                },
                "3º grupo muscular para treinar no dia 6":{
                    TODOS OS EXERCÍCIOS PARA O GRUPO MUSCULAR: 0 SÉRIES
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                    "exercicio para o grupo muscular": numero de series,
                }
            }
        }
        """

        model = LpProblem(name="training-plan-optimization", sense=LpMaximize)

        x = [[[] for _ in range(len(exercise_train[a]))] for a in exercise_train.keys()]

        """
        x terá a estrutura para abrigar o nome das variáveis, separados por [dia de treino][grupo muscular]
        Desta forma, terá a forma:
        [
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> PRIMEIRO DIA
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> SEGUNDO DIA
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> TERCEIRO DIA
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> QUARTO DIA
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> QUINTO DIA
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> SEXTO DIA
            [ 
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> PRIMEIRO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> SEGUNDO GRUPO MUSCULAR
                [nome_do_exercicio_1, nome_do_exercicio_2, nome_do_exercicio_3], -> TERCEIRO GRUPO MUSCULAR
            ], -> SÉTIMO DIA
        ]
        Vale a ressalva que os dias que não tiverem divisão de treino conforme previsão da IA, não entra na lista.
        """

        # Preenche a estrutura de x
        for idx, k in enumerate(exercise_train.keys()):
            for c, i in enumerate(exercise_train[k].keys()):
                for exercise in exercise_train[k][i].keys():
                    var_name = f"{k}_{i}_{exercise}"
                    x[idx][c].append(LpVariable(var_name, lowBound=0, upBound=maxSeriesByExercise, cat='Integer'))
        model += lpSum(x[j][i][k] for j in range(len(x)) for i in range(len(x[j])) for k in range(len(x[j][i])))

        #A soma dos exercícios não deve exceder o tempo de treino
        for a in range(len(x)):
            model += lpSum(x[a][j][i] * duration_exercise
                          for j in range(len(x[a])) for i in
                          range(len(x[a][j]))) <= duration * 60

        #A qnt de séries não ultrapassa 5
        for i in range(len(x)):
            for a in range(len(x[i])):
                for k in range(len(x[i][a])):
                    model += x[i][a][k] <= maxSeriesByExercise


        #A qnt de séries por semana não ultrapassa 12 e deve ser superior a 5
        for muscle_group in muscleGroup:
            model += lpSum(x[i][j][k] for i in range(len(x))
                           for j in range(len(x[i]))
                          for k in range(len(x[i][j])) if f"{muscle_group}_" in str(x[i][j][k])) <= maxSeriesByMuscleGroup
            model += lpSum(x[i][j][k] for i in range(len(x))
                          for j in range(len(x[i]))
                          for k in range(len(x[i][j])) if f"{muscle_group}_" in str(x[i][j][k])) >= minSeriesByMuscleGroup

        model.solve()
        for i in model.variables():
            exercise_train[int(i.name.split("_")[0])][i.name.split("_")[1]][i.name.split("_")[2]] = i.varValue

        return exercise_train

    def showMessage(self, dictData):
        for i in dictData.keys():
            print(f"Treino {i+1}:")
            for a in dictData[i].keys():
                for j in dictData[i][a].keys():
                    if(dictData[i][a][j] > 0):
                        print(f"\t{dictData[i][a][j]}x10-12 - {j}")
