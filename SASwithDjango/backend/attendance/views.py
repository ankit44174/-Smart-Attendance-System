from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from pymongo import MongoClient
import subprocess
import os
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

client = MongoClient('mongodb://localhost:27017/')
db = client['attendance']
collection =db['recognized_faces']



class SignupView(APIView):
    """
    API endpoint for user registration (signup).
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    


class LoginView(APIView):
    """
    API endpoint for user login.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)
    



class UploadVideoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes= (MultiPartParser, FormParser)

    def post(self,request,*args,**kwargs):
        video_file = request.FILES['video'] 
        file_path = default_storage.save(f'media/videos/{video_file.name}', video_file)

        script_path = os.path.abspath("faceRecognitionScript.py")
        video_path = os.path.abspath(file_path)
        session_id = str(uuid.uuid4())  

        try:
            subprocess.run(['C:/Python312/python.exe', script_path, video_path, session_id], check=True)
            return Response({"message": "Video processed successfully.", "session_id": session_id}, status=200)
        except subprocess.CalledProcessError as e:
            return Response({"error": str(e)}, status=500)

class RecognizedFacesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args, **kwargs):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({"error": "Session ID is required."},status=400)

        try:
            faces = list(collection.find({"session_id":session_id}, {"_id": 0, "name": 1}))
            names = [face["name"] for face in faces]
            return Response({"recognized_faces": names}, status=200)
        except Exception as e:
            return Response({"error": str(e)},status=500)
