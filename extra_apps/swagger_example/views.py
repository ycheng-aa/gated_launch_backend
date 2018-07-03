from .models import ExampleUser

from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import ExampleUserSerializer


class ExampleUserViewSet1(viewsets.ModelViewSet):
    queryset = ExampleUser.objects.all()
    serializer_class = ExampleUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """
        CREATE a Example User instance
        ---
        Parameters:
        --
            parameter: username | desc: the user name | type: string | required: true

            parameter: email | desc: the user email | type: string | required: true | location: form

        Examples:
        --
            {
                "username": "test@qq.com",
                "email": "test@qq.com"
            }

        """
        return super(ExampleUserViewSet1, self).create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        GET a User Instance by ID
        ---
        Parameters:
        --
            parameter: ID | description: the primary key of user | type: integer

        Example:
        --
        id:

            1

        """
        return super(ExampleUserViewSet1, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        UPDATE a user instance by all fields
        ---
        Parameters:
        --
            parameter: id | description: primary key | type: integer | filed: query

            parameter: username | description: user name | type: string | field: form

            parameter: email | description: email | type: string | field: form

        Example:
        --
        id:

            3

        data:

            {
                "username": "test_update",
                "email": "test_update@qq.com"
            }

        """
        return super(ExampleUserViewSet1, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE a user instance
        ---
        Parameters:
        --
            parameter: ID | description: the primary key of user | type: integer

        Example:
        --
        id:

            3

        """
        return super(ExampleUserViewSet1, self).destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        GET all user instance
        ---
        Parameters:
        --
            parameter: page | description: how many page to get | type: integer

            parameter: pageSize | description: how many instance in a page | type: integer

        Example:
        --
        page:

            1

        pageSize:

            3

        """
        return super(ExampleUserViewSet1, self).list(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        PARTIAL UPDATE a user instance by all fields
        ---
        Parameters:
        --
            parameter: id | description: primary key | type: integer | filed: query

            parameter: username | description: user name | type: string | field: form

            parameter: email | description: email | type: string | field: form

        Example:
        --
        id:

            3

        data:

            {
                "username": "test_update",
                "email": "test_update@qq.com"
            }

        """
        return super(ExampleUserViewSet1, self).partial_update(request, *args, **kwargs)
